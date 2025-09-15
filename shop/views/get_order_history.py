from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.services.get_order_history import get_order_history








class GetOrderHistoryAPIView(APIView):
   

    def get(self, request):
        user_id = request.user.id
        lang = request.query_params.get("lang", "uz")

        response = get_order_history(user_id, lang)
        if response:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "No orders found."}, status=status.HTTP_404_NOT_FOUND)
       