from payment.actions import request_payer_payment_url, generate_order_action
from payment.models import CustomerOrder
from payment.selectors import get_orders_url_not_generate
from users.actions import add_user_to_default_group
from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)


def request_payment_url_cron():
    """
    Cron job: Generate and request payment URLs for pending orders.

    This scheduled task runs periodically to check for any customer orders
    that have not yet been assigned a payment URL. For each such order, it
    triggers a payment request process via `request_payer_payment_url()`.

    Steps:
      1. Log cron start.
      2. Fetch all orders without payment URLs.
      3. For each order, initiate payment URL request.
      4. Log completion or no-order status.

    Expected behavior:
      - Helps keep payment records updated.
      - Ensures every new order gets a valid payment URL for processing.
    """
    logger.info("Request payment url cron started")
    orders = get_orders_url_not_generate()
    logger.info(f"Request payment url cron started for {orders.count()} orders")
    if orders.exists():
        for order in orders:
            request_payer_payment_url(order.customer)
    else:
        logger.info("🤚 No order found with no url")



def generate_order_for_user_cron():
    """
    Cron job: Automatically generate customer orders for users.

    This job identifies all users who do not yet have an existing
    `CustomerOrder` and creates one for them. If a user is not
    assigned to any group, it automatically assigns them to the
    default group before generating the order.

    Steps:
      1. Log cron start.
      2. Retrieve users without any existing order.
      3. For each user:
         - Assign a default group if missing.
         - Generate a new order via `generate_order_action()`.

    Expected behavior:
      - Keeps user order records synchronized.
      - Ensures every user has at least one active order.
    """
    logger.info("generate_order_for_user_cron started")
    users_without_order = User.objects.exclude(
        id__in=CustomerOrder.objects.values_list("customer__id", flat=True)
    )

    for user in users_without_order:
        if not user.groups.first():
            add_user_to_default_group(user)
            continue
        generate_order_action(user)

