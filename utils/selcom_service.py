import base64

from selcom_apigw_client import apigwClient

from utils.logger import AppLogger  # Custom logger utility


class SelcomApiClient:
    """
    A client class for interacting with the Selcom Payment Gateway API.
    Handles payment processing, order updates, and logging of all operations.
    """

    def __init__(self, get_static_config):
        """
        Initialize the Selcom API client with configuration and order details.

        Args:
            get_static_config: Configuration object containing API settings
        """
        # Initialize logger for tracking all operations
        self.logger = AppLogger(__name__)

        # Store API credentials and configuration
        self.api_Key = get_static_config.api_key
        self.api_secret = get_static_config.secrets_key

        # API endpoint configuration
        self.base_url = get_static_config.base_url
        self.order_path = get_static_config.order_path

        # URL configuration for callbacks
        self.webhook_url = get_static_config.webhook_url
        self.cancel_url = get_static_config.cancel_url
        self.redirect_url = get_static_config.redirect_url

        # Payment configuration
        self.currency = get_static_config.currency
        self.payment_methods = get_static_config.payment_methods
        self.no_of_items = get_static_config.no_of_items

        # Customer/billing information
        self.state_or_region = get_static_config.state_or_region
        self.city = get_static_config.city
        self.country = get_static_config.country

        # Vendor information
        self.vendor_till = get_static_config.vendor_till
        self.remark = get_static_config.remark

    def execute_selcom_payment(self, order):
        """
        Execute a payment transaction through the Selcom API.

        Args:
            order: Order object containing customer and payment details

        Returns:
            dict: Response from the API including status and payment URL if successful
        """
        self.logger.info(f"Starting request payment execution for order: {order.order_id}")
        cancel_url = f"{self.redirect_url}/{order.uuid}/?redirect_status=cancel"
        redirect_url = f"{self.redirect_url}/{order.uuid}/?redirect_status=success"

        # Construct the order payload for the API request
        order_dict = {
            # Vendor and order identification
            "vendor": self.vendor_till,
            "order_id": order.order_id,

            # Customer information
            "buyer_email": order.customer.email,
            "buyer_name": f"{order.customer.first_name} {order.customer.last_name}",
            "buyer_phone": f"{order.customer.phone}",

            # Payment details
            "amount": f"{order.fee.amount}",
            "currency": self.currency,
            "buyer_remarks": self.remark,
            "merchant_remarks": "None",
            "no_of_items": 1,
            "payment_methods": self.payment_methods,

            # Billing address information
            "billing.firstname": order.customer.first_name,
            "billing.lastname": order.customer.last_name,
            "billing.address_1": order.customer.phone,  # Note: Using phone as address_1
            "billing.address_2": self.country,
            "billing.city": self.city,
            "billing.state_or_region": self.state_or_region,
            "billing.country": self.country,
            "billing.phone": order.customer.phone,
            "billing.postcode_or_pobox": order.customer.phone,

            # Encoded callback URLs
            "webhook": base64.b64encode(self.webhook_url.encode()).decode(),
            "cancel_url":base64.b64encode(cancel_url.encode()).decode(),
            "redirect_url": base64.b64encode(redirect_url.encode()).decode(),
        }

        self.logger.debug(f"Order payload: {order_dict}")

        try:
            # Initialize API client and make the request
            client = apigwClient.Client(self.base_url, self.api_Key, self.api_secret)
            response = client.postFunc(self.order_path, order_dict)

            if response['result'] == "FAIL":
                # Handle failed payment response
                json_response = {
                    "order": order.order_id,
                    "msg": response['message'],
                    "result": response['result'],
                    "result_code": response['resultcode'],
                    "decoded_string": "",
                }
                self.logger.error(f"Payment failed for order: {order.order_id}. Response: {response}")

            else:
                # Handle successful payment response
                encoded_string = response['data'][0]['payment_gateway_url']
                decoded_bytes = base64.b64decode(encoded_string)
                decoded_string = decoded_bytes.decode('utf-8')

                json_response = {
                    "msg": response['message'],
                    "result": response['result'],
                    "result_code": response['resultcode'],
                    "url": decoded_string,
                }
                self.logger.info(f"Payment successful for order: {order.order_id}")
                self.update_order(order, response, decoded_string)

            return json_response

        except Exception as e:
            # Handle any exceptions during API communication
            self.logger.error(f"API request failed for order {order.order_id}: {str(e)}")
            raise  # Re-raise the exception after logging

    def update_order(self, order, response, url):
        self.logger.info(f"Updating order {url}")
        """
        Update the order record with the response from Selcom API.

        Args:
            order: Order object to be updated
            response: API response containing transaction details
            url: Payment gateway URL (decoded)

        Raises:
            Exception: If order update fails
        """
        try:
            # Update order with transaction reference and status
            order.reference = response["reference"]
            # order.order_id = self.generated_order_id
            order.resultcode = response["resultcode"]
            order.result = response["result"]
            order.message = response["message"]

            # Store payment gateway details
            order.payment_gateway_url = url
            order.gateway_buyer_uuid = response['data'][0]['gateway_buyer_uuid']
            order.payment_token = response['data'][0]['payment_token']
            order.is_generated = True

            # Persist the updated order
            order.save()
            self.logger.info(f"Order {order.order_id} updated successfully")

        except Exception as e:
            self.logger.error(f"Failed to update order {order.order_id}: {str(e)}")
            raise  # Re-raise the exception after logging
