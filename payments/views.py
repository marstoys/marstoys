
from click_up.views import ClickWebhook
from click_up.models import ClickTransaction
from shop.models import Order
class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):

        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )
        order = Order.objects.get(id=transaction.account_id)
        order.is_paid = True
        order.save()

    def cancelled_payment(self, params):
        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )
        if transaction.state==ClickTransaction.CANCELED:
            order = Order.objects.get(id=transaction.account_id)
            order.is_paid = False
            order.save()
