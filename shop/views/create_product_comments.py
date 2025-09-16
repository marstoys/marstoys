from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.exceptions.error_messages import ErrorCodes
from core.exceptions.exception import CustomApiException
from shop.services.create_product_comments import create_comment_product


class CreateCommentProductAPIView(APIView):
   
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