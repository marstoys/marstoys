from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,serializers
from shop.services.get_order_history import get_order_history


class OrderHistorySerializer(serializers.Serializer):
    class OrderItemSerializer(serializers.Serializer):
        item_id = serializers.IntegerField()
        product_id = serializers.IntegerField()
        product_name = serializers.CharField()
        price = serializers.FloatField()
        quantity = serializers.IntegerField()
    order_id = serializers.IntegerField()
    status = serializers.CharField()
    payment_method = serializers.CharField()
    is_paid = serializers.BooleanField()
    items = OrderItemSerializer(many=True)





class GetOrderHistoryAPIView(APIView):
   

    def get(self, request):
        user_id = request.user.id
        lang = request.query_params.get("lang", "uz")

        response = get_order_history(user_id, lang)
        if response:
            serializer = OrderHistorySerializer(data=response, many=True)
            if serializer.is_valid():
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "No orders found."}, status=status.HTTP_404_NOT_FOUND)
       