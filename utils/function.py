import base64
import nextsms
import uuid
import json
from django.core.files.base import ContentFile
from payment.models import CustomerOrder, OrderStaticConfig
from utils.logger import AppLogger

logger = AppLogger(__name__)

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


def create_file_from_base64(base64_str, ext="jpg"):
    """
    Converts a plain Base64 string (no header) into a Django ContentFile.

    Args:
        base64_str (str): Pure Base64 string (no 'data:...' header).
        ext (str): File extension (default 'mp4').

    Returns:
        ContentFile: ready to assign to a FileField
    """
    if not base64_str:
        logger.warning("No Base64 content received.")
        return None

    try:
        # Create a random filename (e.g. video_<uuid>.mp4)
        filename = f"propert_image_{uuid.uuid4().hex[:8]}.{ext}"

        # Decode the Base64 data and wrap in ContentFile
        file_content = base64.b64decode(base64_str)
        return ContentFile(file_content, name=filename)

    except Exception as e:
        logger.error(f"Failed to decode Base64 file: {e}")
        return None


def check_json_list_type(value):
    if isinstance(value, list):
        return value

    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else None
        except json.JSONDecodeError:
            return None

    return None