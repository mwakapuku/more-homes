from decimal import Decimal

from django.utils import timezone
from requests import Response
from rest_framework import status

from payment.models import CustomerOrderPayment, CustomerOrder, WebhookResponse
from payment.selectors import get_current_static_config, get_group_fee
from users.models import User
from utils.logger import AppLogger
from utils.response_utils import create_response
from utils.selcom_service import SelcomApiClient

logger = AppLogger(__name__)


def create_webhook_response(body, ip):
    try:
        webhook_response = WebhookResponse(response=body, remote_ip=ip)
        webhook_response.save()
        logger.info('Created webhook response')
        return webhook_response
    except Exception as ex:
        logger.info(f'Failed to create webhook response {ex}')
        return None


def create_payment_record(order, payment_data):
    logger.info(f"Starting creation payment records")

    """Create a CustomerOrderPayment record"""
    return CustomerOrderPayment.objects.create(
        order=order,
        result=payment_data['result'],
        resultcode=payment_data['resultcode'],
        transid=payment_data['transid'],
        reference=payment_data['reference'],
        channel=payment_data['channel'],
        amount=Decimal(payment_data['amount']),
        phone=payment_data['phone'],
        payment_status=payment_data.get('payment_status', 'PENDING').upper(),
        orderid=payment_data['order_id']
    )


def request_payment_url(payer: User) -> Response:
    success, response = request_payer_payment_url(payer)
    if success:
        return create_response("Payment url processed successfully", status.HTTP_200_OK, data=response)
    else:
        msg = f"No unpaid orders found for {payer.first_name} {payer.last_name}"
        logger.info(msg)
        return create_response(msg, status.HTTP_400_BAD_REQUEST)


def request_payer_payment_url(user: User):
    name = f"{user.first_name} {user.last_name}"
    logger.info(f"🔥 Start generating payment url request for {name}")
    get_orders = CustomerOrder.objects.filter(is_paid=False, is_generated=False, customer=user)

    total_order = get_orders.count()
    fail_order = 0
    success_order = 0
    logger.info(f"🔥 Total order: {total_order}")

    if get_orders.exists():
        get_static_config = get_current_static_config()
        if get_static_config is None:
            msg = f"🔥 active payment configuration found."
            logger.info(msg)
            return create_response(msg, status.HTTP_500_INTERNAL_SERVER_ERROR)

        initialize_payment = SelcomApiClient(get_static_config)
        for order in get_orders:
            response = initialize_payment.execute_selcom_payment(order)
            logger.info(f"Response from selcom, {response}")
            if not response['result'] == "SUCCESS":
                fail_order = fail_order + 1
                order.message = response
                order.save()

            if response['result'] == "SUCCESS":
                success_order = success_order + 1

        response = {
            "msg": "success",
            "total_order": total_order,
            "generated_order": success_order,
            "non_generated_order": fail_order
        }
        return True, response
    else:
        msg = f"No unpaid orders found for {name}"
        logger.info(msg)
        return False, None


def generate_order_action(user):
    """Get fee"""
    fee = get_group_fee(user.groups.first())
    logger.info(f"{user.username} Group: {user.groups.first()}")

    static_conf = get_current_static_config()
    if fee is None:
        logger.info(f"Fee for the selected group does not found")
    if static_conf is None:
        logger.info(f"Static configuration not found")

    if fee and static_conf:
        logger.info(f"Customer order is created for {user}")
        customer_order = CustomerOrder(
            fee=fee,
            customer=user,
            static_conf=static_conf,
            last_payment_date=timezone.now().date(),
            created_by=user,
            updated_by=user,
        )
        customer_order.save()
        return customer_order
    return None