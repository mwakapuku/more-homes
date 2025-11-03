from payment.actions import request_payer_payment_url, generate_order_action
from payment.models import CustomerOrder
from payment.selectors import get_orders_url_not_generate
from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)


def request_payment_url_cron():
    logger.info("Request payment url cron started")
    orders = get_orders_url_not_generate()
    logger.info(f"Request payment url cron started for {orders.count()}")
    if orders.exists():
        for order in orders:
            request_payer_payment_url(order.customer)
    else:
        logger.info("🤚 No order found with no url")


def generate_order_for_user_cron():
    logger.info("generate_order_for_user_cron started")
    user = User.objects.exclude(id__in=CustomerOrder.objects.values_list("customer__id", flat=True))
    for user in user:
        generate_order_action(user)
