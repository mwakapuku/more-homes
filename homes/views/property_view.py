import json

from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions
from rest_framework.views import APIView

from homes.models import Property
from homes.selectors import get_property_detail, get_property_by_uploader, get_property_to_display
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
        properties = get_property_to_display(request.user)
        total_item = properties.count()
        serializer = PropertySerializer(properties, many=True, context={'request': request})

        logger.info(f"Returning {total_item} properties")
        return create_response("success", status.HTTP_200_OK, total_item=total_item, data=serializer.data)

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


class PropertyDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: PropertySerializer(many=True)},
        tags=["properties"],
        summary="Property Detail",
        description="Returns a single property."
    )
    def get(self, request, uuid, *args):
        logger.info(f"Received GET request for property with ID {uuid}")
        try:
            get_property = get_property_detail(uuid)
            serializer = PropertySerializer(get_property, context={'request': request})
            return create_response("success", status.HTTP_200_OK, data=serializer.data)
        except Property.DoesNotExist:
            msg = f"Property with ID {uuid} not found"
            logger.error(msg)
            return create_response(msg, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            msg = f"Property with ID validation failed: {e}"
            logger.error(msg)
            return create_response(msg, status.HTTP_500_INTERNAL_SERVER_ERROR)


class PropertyOwnerAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: PropertySerializer(many=True)},
        tags=["properties"],
        summary="Uploader Property",
        description="Returns all Uploader Properties."
    )
    def get(self, request, *args):
        logger.info(f"Received GET request on PropertyDetailAPIView by user {request.user}")
        get_properties = get_property_by_uploader(request.user)
        total_item = get_properties.count()
        serializers = PropertySerializer(get_properties, many=True, context={'request': request})
        return create_response("success", status.HTTP_200_OK, total_item=total_item, data=serializers.data)
