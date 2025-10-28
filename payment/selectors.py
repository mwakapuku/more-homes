from payment.models import OrderStaticConfig, Fee, CustomerOrder
from utils.logger import AppLogger

logger = AppLogger(__name__)


def get_current_static_config():
    static_config = OrderStaticConfig.objects.filter(active=True)
    if not static_config.exists():
        return None
    return static_config.first()


def get_group_fee(group):
    get_fee = Fee.objects.filter(group=group)
    if not get_fee.exists():
        return None
    return get_fee.first()


def get_customer_order(order_id):
    """Get the CustomerOrder with payment details"""
    try:
        order = CustomerOrder.objects.get(order_id=order_id)
        logger.info(f"Order with order id: {order_id} found and returned")
        return order
    except CustomerOrder.DoesNotExist:
        logger.error(f"Order not found: {order_id}")
        raise
