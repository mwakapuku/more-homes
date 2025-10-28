import re

from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+255[6-9][0-9]{8}$',
    message="Phone number must be entered in the format: '+2556XXXXXXXX'. Up to 13 digits allowed."
)


def validate_nida_number(nida_number):
    """
    Validate a Tanzanian NIDA number.
    The format is 20 digit.
    """
    pattern = r'^\d{20}'  # Regex for 16 digits and 4 letters
    if re.match(pattern, nida_number):
        return True
    return False


def validate_phone(value):
    """Validate Tanzanian phone numbers starting with +255 and 9 digits."""
    return bool(re.match(r'^\+255\d{9}$', value))
