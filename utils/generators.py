import base64
import random
import uuid
from django.utils import timezone



def generate_short_uuid():
    """
    Generates a shortened version of a UUID (Universally Unique Identifier).

    Returns:
        str: A 28-character uppercase UUID string (first 28 chars of standard UUID)
    """
    return str(uuid.uuid4())[:28].upper()


def generate_order_id():
    from payment.models import OrderNumberGenerator
    """
    Generates a formatted order ID with the following structure:
    MHP-XXX-YYY-ZZZZZZ

    Where:
    - XXX: Day of year (3 digits)
    - YYY: Sequence number (3 digits)
    - ZZZZZZ: Combined date and sequence number (6 digits)

    The ID ensures consistent length and readability with separators.

    Returns:
        str: Formatted order ID string
    """
    # Get current date in YYMMDD format
    date_part = timezone.now().strftime('%y%m%d')

    # Get next sequential number from database
    seq_number = OrderNumberGenerator.get_next_number()

    # Combine date and sequence number
    combined = f"{date_part}{seq_number}"

    # Pad with leading zeros to ensure consistent length (15 chars)
    padded = combined.zfill(15)[-15:]

    # Format into final structure: FRMS-XXX-YYY-ZZZZZZ
    rand1 = random.randint(100, 999)
    rand2 = random.randint(101, 999)
    formatted = f"MHP-{rand1}-{rand2}-{padded[8:]}"

    return formatted