from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import Products
from rest_framework import status
from shop.views.get_all_products_list import ProductsSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class PopularProducts(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve a list of popular products",
        operation_summary="Get Popular Products",
        responses={status.HTTP_200_OK: ProductsSerializer(many=True)}
    )

    def get(self, request):
        popular_products = Products.objects.order_by("-created_datetime")[:30]
        products_data=[]
        for product in popular_products:
            available_colors = [
            {
                "id": product_color.id,
                "color": product_color.get_color_display(),
                "quantity": product_color.quantity,
                "images": [img.image.url for img in product_color.images.all()]
            }
            for product_color in product.colors.all() if product_color.quantity > 0
        ]
            if not available_colors:
                continue
            product_data = {
                "id": product.id,
                "name": product.name ,
                "category": product.category.name if product.category else None,
                "price": product.price,
                "quantity": 0,
                "discount": product.discount,
                "video_url": product.video_url,
                "discounted_price": product.discounted_price,
                "average_rating": product.average_rating,
                "description": product.description ,
                "colors": available_colors,
                "sold_count": product.sold
            }
            products_data.append(product_data)

        serializer = ProductsSerializer(products_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    