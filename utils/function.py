import nextsms

from payment.models import CustomerOrder, OrderStaticConfig


def send_sms_to_user(phone: str, msg: str) -> dict:
    """Send SMS to user using NextSMS gateway.
    Args:
        phone: Recipient's number (format '2557xxxxxxx')
        msg: Message content
    Returns:
        {'msg': 'success', 'results': sms_response}
    """
    sender = nextsms('FadhilaMbura', 'Faramas@2025')
    phone = f"{phone[1:]}"  # Remove leading '2'
    print(f"Sending SMS to User with phone {phone}")
    responses = sender.sendsms(
        message=msg,
        recipients=[phone],
        sender_id="FARAMAS Co"
    )
    return {'msg': 'success', 'results': responses}


def is_customer_paid_func(customer) -> bool:
    """Check if customer has unpaid orders.
    Returns:
        True if unpaid orders exist, False otherwise
    """
    return CustomerOrder.objects.filter(
        is_paid=False,
        customer=customer
    ).exists()


def get_active_static_config():
    """Get the first active static configuration.

    Returns:
        OrderStaticConfig: The first active config instance or None if none exists
    """
    return OrderStaticConfig.objects.filter(active=True).first()


def has_active_static_config() -> bool:
    """Check if any active static configuration exists.

    Returns:
        bool: True if at least one active config exists, False otherwise
    """
    return OrderStaticConfig.objects.filter(active=True).exists()
