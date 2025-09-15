from rest_framework.views import APIView
from rest_framework.response import Response
from shop.services.get_all_products_list import get_all_products_list
from core.exceptions.exception import CustomApiException
from core.exceptions.error_messages import ErrorCodes
from rest_framework import serializers , status

class ProductsSerializer(serializers.Serializer):
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
    images = serializers.ListField(
        child=serializers.URLField()
    )




class ProductListAPIView(APIView):

    def get(self, request):
        category_id = request.query_params.get("category_id")
        lang = request.query_params.get("lang", "uz")

        products = get_all_products_list(category_id, lang)
        if not products:
            raise CustomApiException(ErrorCodes.NOT_FOUND, message="No products found.")

        serializer = ProductsSerializer(products, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
