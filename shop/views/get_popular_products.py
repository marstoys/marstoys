from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import Products
from rest_framework import status
from shop.views.get_all_products_list import ProductsSerializer




class PopularProducts(APIView):

    def get(self, request):
        popular_products = Products.objects.order_by("-created_datetime")[:8]
        serializer = ProductsSerializer(popular_products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)