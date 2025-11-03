from payment.actions import request_payer_payment_url
from payment.selectors import get_orders_url_not_generate
from utils.logger import AppLogger

logger = AppLogger(__name__)


def request_payment_url_cron():
    logger.info("request_payment_url_cron started")
    order = get_orders_url_not_generate()
    if order.exists():
        request_payer_payment_url(order.customer)
    else:
        logger.info("🤚 No order found with no url")


