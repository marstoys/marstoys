from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import *
from click_up import ClickUp
from config import settings
from rest_framework.pagination import PageNumberPagination
# Create your views here.

click_up = ClickUp(service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID)


class CategoryPagination(PageNumberPagination):
    page_size = 100


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductsSerializer

    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        queryset = Products.objects.prefetch_related("images")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class ProductDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = ProductsSerializer
    queryset = Products.objects.all()

    def get_object(self):
        product_id = self.kwargs.get("product_id")
        return get_object_or_404(Products, pk=product_id)


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    pagination_class = CategoryPagination

    def get_queryset(self):
        gender = self.request.query_params.get("gender")
        if gender:
            return Category.objects.filter(gender=gender)
        return Category.objects.all()


class PopularProducts(APIView):
    serializer_class = ProductsSerializer

    def get(self, request):
        popular_products = Products.objects.order_by("-created_at")[:8]
        serializer = self.serializer_class(popular_products, many=True, context={'request': request})
        return Response(serializer.data)


class CommentProductAPIView(APIView):
    serializer_class = CommentProductSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_id")
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
            serializer.save(commented_by=request.user,product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





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

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')

        user_id = request.user.id
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
    serializers = OrderSerializer

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        orders = Order.objects.filter(
            ordered_by_id=user_id,
        )
        serializer = OrderSerializer(orders, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
