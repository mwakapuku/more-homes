from django.contrib.auth.models import Group
from rest_framework import serializers

from users.actions import add_user_to_default_group
from users.models import User
from utils.logger import AppLogger

logger = AppLogger(__name__)

class OTPVerificationSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)
    otp = serializers.CharField(required=True, max_length=6)


class RequestNewOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=6)
    profile_picture_url = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        required=False
    )
    class Meta:
        model = User
        fields = [
            'uuid', 'first_name', 'last_name', 'phone', 'email', 'username', 'location', 'password',
            'profile_picture_url', 'service_charge', 'permissions', 'groups',
        ]

        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'profile': {'required': False, 'allow_null': True},
            'first_name': {'required': False, 'allow_blank': True},
            'last_name': {'required': False, 'allow_blank': True},
            'username': {'required': False, 'allow_blank': True},
            'phone': {'required': False, 'allow_blank': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)  # Pop password if it exists
        email = validated_data.pop('email', None)
        groups = validated_data.pop('groups', None)
        user = User(**validated_data)
        if password and email:
            user.set_password(password)
            user.username = email
            user.email = email
            user.verified = True
        user.save()

        # ✅ Assign provided group(s) or default one
        if groups:
            user.groups.set(groups)
        else:
            add_user_to_default_group(user, "customer")

        return user

    def get_profile_picture_url(self, obj):
        # get image and if no image then return none
        try:
            if obj.profile.url:
                return obj.profile.url
            return None
        except Exception:
            return None

    def get_groups(self, obj):
        """Return a list of group names the user belongs to."""
        return [group.name for group in obj.groups.all()]

    def get_permissions(self, obj):
        """Return a list of permission codenames assigned to the user."""
        all_perms = obj.get_all_permissions()
        cleaned_perms = [perm.split('.', 1)[-1] for perm in all_perms]
        return cleaned_perms

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)