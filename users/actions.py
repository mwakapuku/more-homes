from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group

from utils.logger import AppLogger

logger = AppLogger(__name__)

def change_user_password(user, password):
    user.reset_otp = False
    user.password = make_password(password)
    user.save()


def add_user_to_default_group(user, default_group_name="customer"):
    """
    Assign a user to a default group by name.

    Args:
        user (User): The user instance to assign.
        default_group_name (str): The name of the default group.

    Returns:
        bool: True if group was added successfully, False otherwise.
    """
    try:
        default_group = Group.objects.get(name=default_group_name)
        user.groups.add(default_group)
        logger.info(f"✅ Assigned default group '{default_group_name}' to user '{user.username}'.")
        return True
    except Group.DoesNotExist:
        logger.warning(f"⚠️ Default group '{default_group_name}' does not exist. User '{user.username}' not assigned.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to add user '{user.username}' to group '{default_group_name}': {e}")
        return False
