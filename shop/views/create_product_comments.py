from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status,serializers
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from shop.services.create_product_comments import create_comment_product

class CreateCommentProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    comment = serializers.CharField(max_length=1000)
    rating = serializers.IntegerField(min_value=1, max_value=5)

class CreateCommentProductAPIView(APIView):

    @swagger_auto_schema(
        request_body=CreateCommentProductSerializer,
        responses={
            status.HTTP_201_CREATED: openapi.Response("Comment created successfully."),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Invalid request."),
            status.HTTP_404_NOT_FOUND: openapi.Response("Product not found.")
        }
    )
    def post(self, request):
        product_id = request.data.get("product_id")
        comment = request.data.get("comment")
        rating = request.data.get("rating")
        if not product_id:
            raise CustomApiException(
                ErrorCodes.NOT_FOUND,
                "Product ID is required."
            )

        create_comment_product(
            product_id=product_id,
            comment=comment,
            rating=rating,
            user=request.user
        )
        return Response({"message": "Comment created successfully."}, status=status.HTTP_201_CREATED)