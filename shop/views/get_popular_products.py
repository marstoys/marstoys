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
        popular_products = Products.objects.order_by("-created_datetime")[:8]
        products_data=[]
        for product in popular_products:

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
                "images": [ {
                    "id": image.id,
                    "image": image.image.url,
                    "color": image.get_color_display(),
                    "quantity": image.quantity,
                    } for image in product.images.all()],
                "sold_count": product.sold
            }
            products_data.append(product_data)

        serializer = ProductsSerializer(products_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    