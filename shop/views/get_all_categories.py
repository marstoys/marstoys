from rest_framework.views import APIView
from rest_framework.response import Response
from shop.services.get_all_categories import get_all_categories
from rest_framework import status,serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class CategoryListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    product_count = serializers.IntegerField()



class CategoryListAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve all categories with their product count",
        operation_summary="Get All Categories",
        manual_parameters=[
            openapi.Parameter(
                "gender",
                openapi.IN_QUERY,
                description="Filter categories by gender",
                type=openapi.TYPE_STRING,
                enum=["male", "female", "all"]
            )
        ]
    )

    def get(self, request):
        gender= request.query_params.get("gender", "all")
        response= get_all_categories(gender)
        serializer=CategoryListSerializer(response, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
