from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)


def verify_phone(phone):
    users = User.objects.filter(phone=phone)
    if users.count() > 1:
        logger.error(f"❌Error:Multiple accounts found. for phone: {phone}")
        return False
    return True


def check_user_by_phone(phone):
    logger.debug("🔥 check is user exist with the given phone number")
    return User.objects.filter(phone=phone).exists()


def check_password_match(password, confirm_password):
    logger.debug("🔥 check password match")
    return password == confirm_password


def check_current_password(user, password):
    logger.debug("🔥 check current password")
    return user.check_password(password)


def get_user_phone(phone):
    logger.debug("🔥 get user by phone number")
    return User.objects.filter(phone=phone).first()
