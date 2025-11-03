import json

from decouple import config
from rest_framework import serializers

from homes.actions.property_facility_actions import update_property_facilities, create_property_facilities
from homes.actions.property_image_actions import update_property_images, create_property_images
from homes.models import PropertyImage, FacilityProperty, Property, Facility

base_url = config('BASE_URL')


class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class PropertyFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityProperty
        fields = ["id", "name"]


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ["id", "image", "image_url"]

    def get_image_url(self, obj):
        try:
            if obj.image and hasattr(obj.image, "url"):
                return f"{base_url}{obj.image.url}"
            return None
        except Exception:
            return None


class PropertySerializer(serializers.ModelSerializer):
    uploader = serializers.ReadOnlyField(source="uploader.id")
    facilities = PropertyFacilitySerializer(many=True, read_only=True)
    images = PropertyImageSerializer(many=True, read_only=True)
    thumbnail = serializers.SerializerMethodField()

    uploader_name = serializers.SerializerMethodField()
    uploader_phone = serializers.SerializerMethodField()
    uploader_role = serializers.SerializerMethodField()
    uploader_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            'uuid', "name", "type", "address", "price", "thumbnail", "is_booked", "description", "total_price",
            "latitude", "longitude", "region", "district", "maintenance", "category", "uploader", "uploader_name",
            "uploader_phone", "uploader_role", "uploader_image_url", "created_at", "facilities", "images",
        ]

    def get_uploader_name(self, obj):
        """Return the full name of the uploader, or None if uploader is missing."""
        return f"{obj.uploader.first_name} {obj.uploader.last_name}" if obj.uploader else None

    def get_uploader_phone(self, obj):
        """Return the phone number of the uploader, or None if not available."""
        return getattr(obj.uploader, "phone", None)

    def get_uploader_role(self, obj):
        """Return a comma-separated string of group names the user belongs to."""
        group_name = [group.name for group in obj.uploader.groups.all()]
        if not group_name:
            print("user has no group")
            return None

        return ", ".join(group_name)

    def get_uploader_image_url(self, obj):
        """Return the full URL of the uploader's profile image, or None if not available."""
        try:
            if obj.uploader and obj.uploader.profile:
                return f"{base_url}{obj.uploader.profile.url}"
        except Exception:
            return None
        return None

    def get_thumbnail(self, obj):
        """Return the URL of the first property image as thumbnail, or None if no images exist. use related name"""
        first_image = obj.property_images.first()
        if first_image and first_image.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(first_image.image.url)
            return first_image.image.url
        return None

    # --- CREATE with Base64 images ---
    def create(self, validated_data):
        request = self.context["request"]
        # --- Create property ---
        property_instance = Property.objects.create(**validated_data)

        # --- Parse facilities ---
        facilities_data = []
        raw_facilities = request.data.get("facilities", "[]")
        try:
            facilities_data = json.loads(raw_facilities)
        except Exception:
            pass

        # --- Create facilities ---
        create_property_facilities(facilities_data, property_instance)

        # --- Parse Base64 Images ---
        images_data = request.data.get("images", [])

        # --- Create images from Base64 ---
        create_property_images(property_instance, images_data)

        return property_instance

    # --- UPDATE with Base64 images ---
    def update(self, instance, validated_data):
        request = self.context["request"]

        # --- Parse facilities ---
        facilities_data = []
        raw_facilities = request.data.get("facilities", "[]")
        try:
            facilities_data = json.loads(raw_facilities)
        except Exception:
            pass

        # --- Update property fields ---
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # --- Update facilities ---
        update_property_facilities(facilities_data, instance)

        # --- Parse Base64 Images ---
        images_data = request.data.get("images", [])

        # --- Update property images ---
        update_property_images(images_data, instance)

        return instance
