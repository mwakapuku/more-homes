from decimal import Decimal

from django.contrib.humanize.templatetags.humanize import intcomma
from rest_framework import serializers

from .models import CustomerOrder, CustomerOrderPayment


class PaymentResponseSerializer(serializers.Serializer):
    """
    Serializer for handling payment gateway responses.
    It defines the expected fields from a payment gateway callback
    and includes validation for the 'amount' field.
    """
    result = serializers.CharField(max_length=20)
    resultcode = serializers.CharField(max_length=10, required=False)
    order_id = serializers.CharField(max_length=50)
    transid = serializers.CharField(max_length=50)
    reference = serializers.CharField(max_length=50)
    channel = serializers.CharField(max_length=20)
    amount = serializers.CharField(max_length=20)
    phone = serializers.CharField(max_length=20)

    def validate_amount(self, value):
        """
        Custom validation for the 'amount' field.
        Ensures the amount is a valid positive decimal number.
        """
        try:
            amount = Decimal(value)
            if amount <= 0:
                # Raise a validation error if the amount is not positive
                raise serializers.ValidationError("Amount must be positive")
            return str(amount)
        except (ValueError, TypeError):

            raise serializers.ValidationError("Invalid amount format")


class PaymentLogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerOrderPayment
        fields = '__all__'


class CustomerOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomerOrder model.
    It prepares CustomerOrder model instances for API responses,
    including custom representations for 'amount' and 'interval'.
    """
    amount = serializers.SerializerMethodField()
    interval = serializers.SerializerMethodField()

    class Meta:
        """
        Meta class to define the model and fields for the serializer.
        """
        model = CustomerOrder
        fields = (
            'order_id',
            'last_payment_date',
            'next_payment_date',
            'created',
            'amount',
            'interval',
            'is_paid',
            'is_generated',
            'payment_gateway_url',
            'reference',
            'result'
        )

    def get_amount(self, obj):
        """
        Retrieves the 'amount' from the associated Fee model instance
        and formats it with comma separators for readability (e.g., 1,000,000).
        Assumes `obj.fee` is a related object with an `amount` attribute.
        """
        # Ensure that obj.fee exists and has an amount attribute
        if hasattr(obj, 'fee') and hasattr(obj.fee, 'amount'):
            return intcomma(obj.fee.amount)
        return None

    def get_interval(self, obj):
        """
        Retrieves the 'interval' from the associated Fee model instance.
        Assumes `obj.fee` is a related object with an `interval` attribute.
        """
        # Ensure that obj.fee exists and has an interval attribute
        if hasattr(obj, 'fee') and hasattr(obj.fee, 'interval'):
            return obj.fee.interval
        return None