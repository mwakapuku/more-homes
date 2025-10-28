import json

from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.views import APIView

from homes.models import Property
from homes.serializers import PropertySerializer
from utils.logger import AppLogger
from utils.response_utils import create_response

logger = AppLogger(__name__)


class PropertyAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: PropertySerializer(many=True)},
        tags=["properties"],
        summary="List of Properties",
        description="Returns a list of all properties."
    )
    def get(self, request, *args):
        logger.info(f"Received GET request on PropertyAPIView by user {request.user}")
        properties = (
            Property.objects.all().
            filter(is_booked=False).
            exclude(uploader=request.user).
            prefetch_related('uploader')
        )
        serializer = PropertySerializer(properties, many=True, context={'request': request})

        logger.info(f"Returning %d properties {len(serializer.data)}")

        return create_response("success", status.HTTP_200_OK, data=serializer.data)

    # @payment_required(['broker', 'property owner', 'customer'])
    @extend_schema(
        responses={200: PropertySerializer(many=True)},
        tags=["properties"],
        summary="Create new Property",
        description="Create a new property and return the new property. Only user paid subscription will be able to add"
    )
    def post(self, request, *args, **kwargs):
        logger.info(f"Received POST request on PropertyAPIView by user{request.user}")
        try:
            request.data.get('facilities', [])
        except (TypeError, json.JSONDecodeError) as e:
            msg = f"Invalid facilities JSON: %s {e}"
            logger.error(msg)
            return create_response(msg, status.HTTP_400_BAD_REQUEST)

        images_data = request.FILES.getlist('images')
        logger.debug(f"Number of images received: {len(images_data)}")

        serializer = PropertySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            property_obj = serializer.save(uploader=request.user)
            logger.info(f"Property created with ID: {property_obj.id}")
            return create_response("success", status.HTTP_200_OK, data=request.data)

        msg = f"Property creation failed: {serializer.errors}"
        logger.warning(f"Property creation failed: {serializer.errors}")
        return create_response(msg, status.HTTP_400_BAD_REQUEST)
