from rest_framework.response import Response
from rest_framework.views import APIView
from shop.models import Products
from rest_framework import status
from shop.views.get_all_products_list import ProductsSerializer




class PopularProducts(APIView):

    def get(self, request):
        lang = request.query_params.get("lang", "uz")
        popular_products = Products.objects.order_by("-created_datetime")[:8]
        products_data=[]
        for product in popular_products:

            product_data = {
                "id": product.id,
                "name": product.name if lang == "uz" else product.name_ru if lang == "ru" else product.name_en,
                "category": product.category.name if lang == "uz" else product.category.name_ru if lang == "ru" else product.category.name_en,
                "price": product.price,
                "quantity": product.quantity,
                "discount": product.discount,
                "video_url": product.video_url,
                "discounted_price": product.discounted_price,
                "average_rating": product.average_rating,
                "description": product.description if lang == "uz" else product.description_ru if lang == "ru" else product.description_en,
                "images": [ image.image.url for image in product.images.all()],
                "sold_count": product.sold
            }
            products_data.append(product_data)

        serializer = ProductsSerializer(products_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)