from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.services.get_product_details import get_product_details
from shop.views.get_all_products_list import ProductsSerializer




class ProductDetailsAPIView(APIView):

    def get(self, request):
        product_id = request.query_params.get("product_id")
        product = get_product_details(product_id)
        serializer = ProductsSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)



