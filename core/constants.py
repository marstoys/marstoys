from click_up import ClickUp
from decouple import config
CLICK_SERVICE_ID = config("CLICK_SERVICE_ID")
CLICK_MERCHANT_ID = config("CLICK_MERCHANT_ID")

click_up = ClickUp(service_id=CLICK_SERVICE_ID, merchant_id=CLICK_MERCHANT_ID)
