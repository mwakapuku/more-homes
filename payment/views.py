from django.db import transaction
from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from payment.actions import create_payment_record, request_payment_url, create_webhook_response
from payment.models import CustomerOrder, CustomerOrderPayment
from payment.selectors import get_customer_order
from payment.serializer import PaymentResponseSerializer, PaymentLogsSerializer, CustomerOrderSerializer
from utils.logger import AppLogger
from utils.response_utils import create_response

logger = AppLogger(__name__)


def payment_redirect(request, uuid):
    redirect_status = request.GET.get('status')
    print(f"User redirected with to {redirect_status}")
    try:
        get_order = CustomerOrder.objects.get(uuid=uuid)
        context = {
            'success': True,
            'order': get_order,
            'status': redirect_status,
        }
    except CustomerOrder.DoesNotExist:
        context = {
            'msg': 'Order does not exist',
            'success': False,
            'status': redirect_status,
        }
    return render(request, "payment/redirect-page.html", context)

@extend_schema(exclude=True)
class PaymentWebhookApiView(APIView):
    # permission_classes = [WebhookPermission]
    def post(self, request):
        logger.info("🔥 Payment webhook received")
        serializer = PaymentResponseSerializer(data=request.data)
        if not serializer.is_valid():
            msg = f"Invalid payment webhook data: {serializer.errors}"
            logger.error(msg)
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        # before processing the data first save the request body
        webhook_res = create_webhook_response(request.data, request.META.get("REMOTE_ADDR", "0.0.0.0"))
        if serializer.is_valid() and webhook_res is not None:
            try:
                with transaction.atomic():
                    payment_data = serializer.validated_data
                    order = get_customer_order(payment_data['order_id'])
                    create_payment_record(order, payment_data)

                    # set webhook response processed to true
                    webhook_res.processed = True
                    webhook_res.save()

                    logger.info(
                        f"Payment processed | "
                        f"Order: {order.order_id} | "
                        f"Amount: {payment_data['amount']} | "
                        f"Status: {payment_data.get('payment_status', 'PENDING')}"
                    )
                    return create_response("Payment Processed successfully", status.HTTP_200_OK)

            except CustomerOrder.DoesNotExist:
                logger.error(f"Order not found: {payment_data['order_id']}")
                msg = f"Order not found: {payment_data['order_id']}"
                return create_response(msg, status.HTTP_404_NOT_FOUND)

            except Exception as e:
                logger.error(f"Error processing payment: {str(e)}")
                msg = f"Error processing payment: {str(e)}"
                return create_response(msg, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return create_response("Payment process failed", status.HTTP_400_BAD_REQUEST)


class CustomerOrderApiView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomerOrderSerializer

    @extend_schema(
        request=CustomerOrderSerializer,
        responses={
            200: {"msg": "Customer order retrieved successfully"},
            400: "Bad request - invalid request",
            404: "Customer with the given name does not have any order",
        },
        tags=["payment"],
        summary="Get customer order",
        description="This return the list of all orders belong to authenticated customer",
    )

    def get(self, request):
        get_customer = CustomerOrder.objects.filter(customer=request.user)
        if get_customer:
            serializer = CustomerOrderSerializer(get_customer, many=True)
            msg = "Customer order retrieved successfully"
            return create_response(msg, status.HTTP_200_OK, data=serializer.data)
        else:
            msg = f"Customer {request.user.first_name} {request.user.last_name} does not have any order"
            logger.error(msg)
            return create_response(msg, status.HTTP_404_NOT_FOUND)


class CustomerPaymentLogsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentLogsSerializer
    @extend_schema(
        request=CustomerOrderSerializer,
        responses={
            200: {"msg": "Customer payment history retrieved successfully"},
            400: "Bad request - invalid request",
            500: "active payment configuration found.",
        },
        tags=["payment"],
        summary="Request Payment URL",
        description="Request the payment url from Third part",
    )
    def get(self, request):
        order_id = request.query_params.get('order_id')
        user = request.user

        payments = CustomerOrderPayment.objects.filter(order__customer=user).order_by('-created')

        if order_id:
            payments.filter(order__order_id=order_id)

        serializer = self.serializer_class(payments, many=True)
        return create_response("Success", status.HTTP_200_OK, data=serializer.data)


class RequestPaymentUrlApiView(APIView):
    permission_classes = [IsAuthenticated]
    @extend_schema(
        request=CustomerOrderSerializer,
        responses={
            200: {"msg": "Payment url processed successfully"},
            400: "Bad request - invalid request",
            404: "Customer with the given name does not have any order",
        },
        tags=["payment"],
        summary="Get Customer Payment history and specific by specifying order_id",
        description="This return the list of all payment history belong to authenticated customer ",
    )
    def get(self, request):
        return request_payment_url(request.user)
