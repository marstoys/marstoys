from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.services.exel_import import save_excel_to_db

class ExcelUploadView(APIView):
    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get("file")
        if not excel_file:
            return Response({"error": "Fayl topilmadi"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rows = save_excel_to_db(excel_file)
            return Response({"status": "ok", "rows": rows}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

