from django.urls import path

from payment.views import (
    payment_redirect, PaymentWebhookApiView, CustomerOrderApiView, CustomerPaymentLogsAPIView,
    RequestPaymentUrlApiView
)

urlpatterns = [
    path('redirect', payment_redirect, name='payment_redirect'),
    path('webhookurl/mhp/f1cp8vf&6v1w_3mobxs5bb0j', PaymentWebhookApiView.as_view(), name='payment-webhook-api'),
    path('my-order', CustomerOrderApiView.as_view(), name='payment-webhook-api'),
    path('payment-history', CustomerPaymentLogsAPIView.as_view(), name='payment-webhook-api'),
    path('request-payment-url', RequestPaymentUrlApiView.as_view(), name='payment-webhook-api'),
]
