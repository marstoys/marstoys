from django.db.models import Q, Sum
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
from .serializer import *
from click_up import ClickUp
from config import settings

# Create your views here.
click_up = ClickUp(service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID)


class ProductListAPIView(generics.ListAPIView):
    queryset = Products.objects.prefetch_related("images").all()
    serializer_class = ProductsSerializer
    comments = CommentProducts.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        search = self.request.query_params.get("search")
        cost_min = self.request.query_params.get("cost_min")
        cost_max = self.request.query_params.get("cost_max")

        if cost_min and cost_max:
            queryset = queryset.filter(price__gte=cost_min, price__lte=cost_max)
        elif cost_min:
            queryset = queryset.filter(price__gte=cost_min)
        elif cost_max:
            queryset = queryset.filter(price__lte=cost_max)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        if category:
            queryset = queryset.filter(category__name=category)
        return queryset


class ProductDetailsAPIView(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Products, pk=product_id)
        serializer = ProductsSerializer(product)
        return Response(serializer.data)


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class PopularProducts(APIView):
    serializer_class = ProductsSerializer

    def get(self, request):
        popular_products = Products.objects.order_by("-created_at")[:5]
        serializer = self.serializer_class(popular_products, many=True)
        return Response(serializer.data)
class CommentProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentProductSerializer

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        comment = request.data.get("comment")
        rating = request.data.get("rating")

        data = {
            "product": product.id,
            "comment": comment,
            "rating": rating,
        }

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save(commented_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCommentProductAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentProductSerializer

    def get_queryset(self):
        product_id = self.request.data.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        return CommentProducts.objects.filter(product=product)

class ViewCartProductsAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductsSerializer

    def get_queryset(self):
        user = self.request.user
        return Products.objects.filter(cartproduct__carted_by=user)


class OrderCreateAPIView(generics.CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        for item in order.items.all():
            product = item.product
            product.quantity -= item.quantity
            product.save(update_fields=["quantity"])
        result = {"order": serializer.data}
        if serializer.data.get('payment_method') == "karta":
            payment_link = click_up.initializer.generate_pay_link(
                id=serializer.data.get('id'),
                amount=serializer.data.get('total_price'),
                return_url="https://toysmars.uz"
            )
            order.payment_link = payment_link
            order.save(update_fields=["payment_link"])
            result["payment_link"] = payment_link
        return Response(result, status=status.HTTP_201_CREATED)


class PermissionToCommentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = PermissionToCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.id
        product_id = serializer.validated_data["product_id"]

        exists = Order.objects.filter(
            ordered_by_id=user_id,
            status="delivered",
            items__product_id=product_id
        ).exists()

        if exists:
            return Response({"message": True}, status=status.HTTP_200_OK)

        return Response({"message": False}, status=status.HTTP_403_FORBIDDEN)


class GetOrderHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializers=OrderSerializer
    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        orders = Order.objects.filter(
            ordered_by_id=user_id,
        )
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



def sales_chart(request):
    sales_data = (
        Order.objects.values("created_at__date")
        .annotate(total_sales=Sum("total_price"))
        .order_by("created_at__date")
    )

    dates = [item["created_at__date"] for item in sales_data]
    sales = [item["total_sales"] for item in sales_data]

    plt.figure(figsize=(8, 4))
    plt.bar(dates, sales, color="b", label="Sales")

    plt.xlabel("Sana")
    plt.ylabel("Sotuv summasi")
    plt.title("Sotuvlar statistikasi")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.xticks(rotation=45)

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode("utf-8")

    return render(request, "admin/sales_chart.html", {"chart": graph})
