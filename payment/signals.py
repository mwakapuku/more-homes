from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from payment.models import CustomerOrder, CustomerOrderPayment
from payment.selectors import get_group_fee, get_current_static_config
from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def create_user_order_on_group_add(sender, instance, action, **kwargs):
    if action == "post_add":
        """Get fee"""
        fee = get_group_fee(instance.groups.all().first())
        static_conf = get_current_static_config()
        if fee is None:
            logger.info(f"Fee for the selected group does not found")
        if static_conf is None:
            logger.info(f"Static configuration not found")

        if fee and static_conf:
            logger.info(f"Customer order is created for {instance}")
            customer_order = CustomerOrder(
                fee=fee,
                customer=instance,
                static_conf=static_conf,
                last_payment_date=timezone.now().date(),
                created_by=instance,
                updated_by=instance,
            )
            customer_order.save()


@receiver(post_save, sender=CustomerOrderPayment)
def update_customer_order_on_payment(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Customer order payment created for {instance}")
        if instance.order:
            if instance.payment_status == "COMPLETED" and instance.result == "SUCCESS":
                logger.info(f"Payment completed for order {instance.order.order_id}")
                instance.order.is_paid = True
                instance.order.save()
        else:
            logger.error(f"Payment saved successfully but order is not updated")
