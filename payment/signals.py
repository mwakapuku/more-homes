from datetime import timedelta

from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

from payment.actions import generate_order_action
from payment.models import CustomerOrderPayment
from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)


@receiver(m2m_changed, sender=User.groups.through)
def create_user_order_on_group_add(sender, instance, action, **kwargs):
    if action == "post_add":
        generate_order_action(instance)


@receiver(post_save, sender=CustomerOrderPayment)
def update_customer_order_on_payment(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Customer order payment created for {instance}")
        if instance.order:
            if instance.payment_status == "COMPLETED" and instance.result == "SUCCESS":
                logger.info(f"Payment completed for order {instance.order.order_id}")
                instance.order.is_paid = True
                instance.order.next_payment_date = instance.created_at + timedelta(days=30)
                instance.order.save()
        else:
            logger.error(f"Payment saved successfully but order is not updated")
