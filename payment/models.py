import uuid
from datetime import timedelta

from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models

from utils.generators import generate_order_id


class OrderNumberGenerator(models.Model):
    last_number = models.PositiveBigIntegerField(default=0)

    @classmethod
    def get_next_number(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        obj.last_number += 1
        obj.save()
        return obj.last_number


class AuditModel(models.Model):
    """
    Abstract base class for tracking who created/updated an object
    and when it was created/updated.
    """
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        help_text="User who created this record"
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        help_text="User who last updated this record"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Fee(AuditModel):
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, related_name="fees_group")
    interval = models.IntegerField(validators=[MinValueValidator(30)])
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group}"

    class Meta:
        db_table = "Fee"
        verbose_name_plural = "Subscription Fee"
        verbose_name = "Subscription"


class OrderStaticConfig(AuditModel):
    CURRENCY_CHOICES = (
        ('TZS', 'Tanzanian Shillings'),
        ('usd', 'US Dollar')
    )
    METHODS_CHOICES = (
        ('ALL', 'All'),
        ('MOBILEONLY', 'Mobile Only')
    )
    vendor_till = models.CharField(max_length=50)
    remark = models.CharField(max_length=50, default="Payment For mobile application")
    country = models.CharField(max_length=50, default="TZ")
    city = models.CharField(max_length=50, default="Dar es salaam")
    state_or_region = models.CharField(max_length=50, default="DA")
    currency = models.CharField(max_length=15, choices=CURRENCY_CHOICES)
    payment_methods = models.CharField(max_length=15, choices=METHODS_CHOICES)
    no_of_items = models.PositiveIntegerField(default=1)
    api_key = models.CharField(max_length=150)
    secrets_key = models.CharField(max_length=150)
    base_url = models.URLField()
    webhook_url = models.URLField()
    callback_url = models.URLField()
    redirect_url = models.URLField()
    cancel_url = models.URLField()
    order_path = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.vendor_till}"

    class Meta:
        db_table = "order_static_config"
        verbose_name_plural = "Selcom Params"
        verbose_name = "Selcom Params"


class CustomerOrder(AuditModel):
    order_id = models.CharField(max_length=60, unique=True)
    customer = models.ForeignKey('users.User', on_delete=models.RESTRICT, related_name='customers_orders')
    static_conf = models.ForeignKey(OrderStaticConfig, null=True, on_delete=models.SET_NULL, related_name='conf_orders')
    fee = models.ForeignKey(Fee, on_delete=models.RESTRICT, related_name='customer_fee')
    is_paid = models.BooleanField(default=False)
    is_generated = models.BooleanField(default=False)
    last_payment_date = models.DateField()
    next_payment_date = models.DateField()

    # this is for store when the request successfully handled
    reference = models.CharField(max_length=60)
    resultcode = models.CharField(max_length=60)
    result = models.CharField(max_length=60)
    message = models.CharField(max_length=60)
    gateway_buyer_uuid = models.CharField(max_length=60)
    payment_token = models.CharField(max_length=60)
    qr = models.CharField(max_length=60)
    payment_gateway_url = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.customer}"

    def save(self, *args, **kwargs):
        if self.last_payment_date:
            self.next_payment_date = self.last_payment_date + timedelta(days=30)
        if not self.order_id:
            self.order_id = generate_order_id()
        super(CustomerOrder, self).save(*args, **kwargs)

    class Meta:
        db_table = "customer_order"
        verbose_name_plural = "Customer Orders"
        verbose_name = "Customer Order"


class CustomerOrderPayment(AuditModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    payment_status_choice = (
        ("COMPLETED", "COMPLETED"),
        ("CANCELLED", "CANCELLED"),
        ("PENDING", "PENDING"),
        ("USERCANCELED", "USERCANCELED"),
    )
    resulty_choices = (
        ("SUCCESS", "SUCCESS"),
        ("FAIL", "FAIL"),
    )
    order = models.ForeignKey(CustomerOrder, on_delete=models.RESTRICT, related_name='order_payments')
    result = models.CharField(max_length=20, choices=resulty_choices)
    resultcode = models.CharField(max_length=20)
    transid = models.CharField(max_length=50)
    reference = models.CharField(max_length=50)
    channel = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20, choices=payment_status_choice)
    orderid = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.order}"

    def save(self, *args, **kwargs):
        if self.order:
            self.order.is_paid = True
            self.order.save()
        super(CustomerOrderPayment, self).save(*args, **kwargs)

    class Meta:
        db_table = "payment"
        verbose_name_plural = "Subscription Payments"
        verbose_name = "Payment"


class WebhookResponse(AuditModel):
    response = models.TextField()
    remote_ip = models.GenericIPAddressField()
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.remote_ip}"
