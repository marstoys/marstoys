from click_up import ClickUp
from decouple import config
from rest_framework.pagination import PageNumberPagination
CLICK_SERVICE_ID = config("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = config("CLICK_MERCHANT_ID")

click_up = ClickUp(service_id=CLICK_SERVICE_ID, merchant_id=CLICK_MERCHANT_ID)
class CustomPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = 'page_size'
    max_page_size = 1000