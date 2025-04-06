from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *
from rest_framework.serializers import Serializer, IntegerField
User = get_user_model()

class ImageProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProducts
        fields = ["image"]

class ProductsSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = [
            "id", "name", "price", "images", "description",
            "discount", "quantity", "category", "discounted_price",
            "average_rating", "sold", "video_url"
        ]

    def get_name(self, obj):
        request = self.context.get("request")
        lang = request.query_params.get("lang") if request else None

        if lang == "ru":
            return obj.name_ru
        elif lang == "en":
            return obj.name_en
        return obj.name

    def get_description(self, obj):
        request = self.context.get("request")
        lang = request.query_params.get("lang") if request else None

        if lang == "ru":
            return obj.description_ru
        elif lang == "en":
            return obj.description_en
        return obj.description

    def get_images(self, obj):
        return [
            self._make_https(img.image.url)
            for img in obj.images.all()
        ]

    def _make_https(self, url):
        if url.startswith("http://"):
            return url.replace("http://", "https://")
        return url

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'gender', 'name', 'product_count']

    def get_name(self, obj):
        request = self.context.get("request")
        lang = request.query_params.get("lang") if request else None

        if lang == "ru":
            return obj.name_ru
        elif lang == "en":
            return obj.name_en
        return obj.name

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

    def get_product_details(self, obj):
        return {
            "id": obj.product.id,
            "title": obj.product.name_uz,
            "price": obj.product.price
        }

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    ordered_by = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields ='__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        if not validated_data.get('ordered_by') and request:
            validated_data['ordered_by'] = request.user
        buyer_name = validated_data.get('buyer_name')
        buyer_surname = validated_data.get('buyer_surname')
        buyer_number = validated_data.get('buyer_number')
        user = User.objects.get(phone_number=buyer_number)
        user.first_name = buyer_name
        user.last_name = buyer_surname
        user.save()
        items_data = validated_data.pop('items')
        order = Order.objects.create( **validated_data)
        for item_data in items_data:
            product = item_data.get("product")
            quantity = item_data.get("quantity", 1)
            price = product.discounted_price if product else 0

            total_price = quantity * price


            OrderItem.objects.create(order=order, total_price=total_price, **item_data)

        return order


class CommentProductSerializer(serializers.ModelSerializer):
    first_name = serializers.ReadOnlyField(source="commented_by.first_name")

    class Meta:
        model = CommentProducts
        fields = ["id", "comment", "rating", "product", "first_name", "created_at"]
        extra_kwargs = {
            'commented_by': {'read_only': True},
            'product': {'read_only': True},
        }

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            validated_data["user"] = request.user
        return super().create(validated_data)

class LikedProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LikedProducts
        fields = "__all__"





class PermissionToCommentSerializer(Serializer):
    product_id = IntegerField()