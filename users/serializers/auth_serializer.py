from rest_framework import serializers

from users.models import User


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
    groups = serializers.SerializerMethodField()
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
        user = User(**validated_data)
        if password and email:
            user.set_password(password)
            user.username = email
            user.email = email
            user.verified = True
        user.save()
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