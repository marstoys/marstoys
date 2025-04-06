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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        categories = self.get_queryset()

        grouped = {
            'male': [],
            'female': [],
            'all':[],
        }

        for category in categories:
            category_data = CategorySerializer(category).data
            if category.gender == 'male':
                grouped['male'].append(category_data)
            elif category.gender=='female':
                grouped['female'].append(category_data)
            else:
                grouped['all'].append(category_data)




        response_data = {
            "count": len(categories),
            "next": None,
            "previous": None,
            "results": grouped
        }

        return Response(response_data)

class PopularProducts(APIView):
    serializer_class = ProductsSerializer

    def get(self, request):
        popular_products = Products.objects.order_by("-created_at")[:5]
        serializer = self.serializer_class(popular_products, many=True)
        return Response(serializer.data)
class CommentProductAPIView(APIView):
    serializer_class = CommentProductSerializer

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
            serializer.save(commented_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViewCommentProductAPIView(generics.ListAPIView):
    serializer_class = CommentProductSerializer

    def get_queryset(self):
        product_id = self.kwargs.get("product_id")
        product = get_object_or_404(Products, id=product_id)
        return CommentProducts.objects.filter(product=product)




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


