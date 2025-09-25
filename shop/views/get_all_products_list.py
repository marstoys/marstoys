from rest_framework.views import APIView
from rest_framework.response import Response
from shop.services.get_all_products_list import get_all_products_list
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
from rest_framework import serializers , status
from core.constants import CustomPagination

class ProductsSerializer(serializers.Serializer):
    class ProductImages(serializers.Serializer):
        id = serializers.IntegerField()
        image = serializers.URLField()
        color = serializers.CharField(max_length=20)
    id= serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    category = serializers.CharField(max_length=255)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    quantity= serializers.IntegerField()
    discount = serializers.IntegerField()
    video_url = serializers.URLField(required=False, allow_blank=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1)
    description = serializers.CharField()
    images = ProductImages(many=True)
    sold_count = serializers.IntegerField()




class ProductListAPIView(APIView):
    pagination_class = CustomPagination
    def get(self, request):
        category_id = request.query_params.get("category_id")

        products = get_all_products_list(category_id)
        if not products:
            raise CustomApiException(ErrorCodes.NOT_FOUND, message="No products found.")

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request, view=self)
        
        serializer = ProductsSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
