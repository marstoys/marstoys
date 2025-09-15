from rest_framework.views import APIView
from rest_framework.response import Response
from shop.services.get_all_categories import get_all_categories
from rest_framework import status,serializers


class CategoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    product_count = serializers.IntegerField()



class CategoryListAPIView(APIView):

    def get(self, request):
        lang= request.query_params.get("lang", "uz")
        gender= request.query_params.get("gender", "all")
        response= get_all_categories(lang, gender)
        serializer=CategoryListSerializer(response, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
