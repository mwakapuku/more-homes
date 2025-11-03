from django.contrib import admin

from payment.models import CustomerOrderPayment, CustomerOrder, OrderStaticConfig, Fee, WebhookResponse


# Register your models here.
@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('group', 'amount', 'interval', 'active')
    list_filter = ('group', 'active')
    search_fields = ('group',)
    ordering = ('group',)


@admin.register(OrderStaticConfig)
class OrderStaticConfigAdmin(admin.ModelAdmin):
    list_display = (
        'vendor_till', 'currency', 'payment_methods', 'active', 'created_at', 'updated_at'
    )
    list_filter = ('currency', 'payment_methods', 'active')
    search_fields = ('vendor_till', 'api_key', 'secrets_key')
    readonly_fields = ('created_at', 'updated_at', 'uuid')


@admin.register(CustomerOrder)
class CustomerOrderAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 'fee', 'is_paid', 'last_payment_date', 'next_payment_date',
        'reference', 'resultcode', 'result', 'message'
    )
    list_filter = ('is_paid', 'last_payment_date', 'next_payment_date')
    search_fields = (
        'customer__username', 'customer__email', 'reference', 'gateway_buyer_uuid'
    )
    autocomplete_fields = ('customer', 'static_conf', 'fee')
    raw_id_fields = ('customer', 'static_conf', 'fee')
    readonly_fields = (
        'created_at', 'updated_at', 'reference', 'resultcode', 'result','is_paid', 'is_generated',
        'message', 'gateway_buyer_uuid', 'payment_token', 'qr', 'payment_gateway_url', 'uuid', 'order_id'
    )


@admin.register(CustomerOrderPayment)
class CustomerOrderPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'order', 'amount', 'payment_status', 'result', 'transid', 'phone', 'created_at'
    )
    list_filter = ('payment_status', 'result', 'channel')
    search_fields = ('order__order_id', 'transid', 'reference', 'phone')
    raw_id_fields = ('order',)
    readonly_fields = ('uuid', 'created_at', 'updated_at', 'amount')


@admin.register(WebhookResponse)
class WebhookResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'remote_ip', 'processed', 'created_at', 'updated_at')
    list_filter = ('processed', 'remote_ip', 'created_at')
    search_fields = ('remote_ip', 'response')
    readonly_fields = ('response', 'remote_ip', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    list_editable = ('processed',)

    fieldsets = (
        ('Webhook Information', {
            'fields': ('remote_ip', 'response', 'processed')
        }),
        ('Audit Info', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
