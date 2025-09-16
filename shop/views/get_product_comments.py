from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status,serializers
from shop.services.get_product_comments import get_product_comments


class GetProductCommentsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    text = serializers.CharField()
    rating = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    
    
    
class ProductComments(APIView):

    def get(self, request, product_id):

        comments = get_product_comments(product_id)
        serializer = GetProductCommentsSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)