from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from core.constants import COLOR_CHOICES
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from users.models import CustomUser



class CreateCartProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    color = serializers.ChoiceField(choices=[choice[0] for choice in COLOR_CHOICES])
    
    
    
class CreateCartProductView(APIView):
    @swagger_auto_schema(
        operation_description="Add a product to the user's cart",
        operation_summary="Create Cart Product",
        request_body=CreateCartProductSerializer,
        responses={
            status.HTTP_200_OK: openapi.Response("Product added to cart successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid input."),
            status.HTTP_404_NOT_FOUND: openapi.Response("Product not found.")
        }
    )
    def post(self, request):
        user_id = request.user.id
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            raise CustomApiException(ErrorCodes.UNAUTHORIZED,message="User not found.")
        serializer = CreateCartProductSerializer(data=request.data)
        if serializer.is_valid():
            from shop.services.create_cart_product import create_cart_product
            create_cart_product(user_id, serializer.validated_data)
            return Response({"message": "Product added to cart successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    