from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from shop.services.get_cart_product import get_cart_product
from shop.views.get_all_products_list import ProductsSerializer


class GetCartProductAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve all products in the authenticated user's cart",
        operation_summary="Get Cart Products",
        responses={
            status.HTTP_200_OK: ProductsSerializer(many=True),
            status.HTTP_404_NOT_FOUND: openapi.Response("The cart is empty.")
        }
    )
    def get(self, request):
        user_id = request.user.id
        cart_products = get_cart_product(user_id)
        return Response(cart_products, status=status.HTTP_200_OK)
    