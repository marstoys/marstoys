from rest_framework import  status

from rest_framework.response import Response
from rest_framework.views import APIView
from shop.services.create_order import create_order
# Create your views here.






class OrderCreateAPIView(APIView):

    def post(self, request):
        user_id= request.user.id
        data = request.data
        payment_link = create_order(data,user_id)
        if payment_link:
            return Response({"payment_link": payment_link}, status=status.HTTP_201_CREATED)
        return Response({"success": "Order created successfully"}, status=status.HTTP_200_OK)