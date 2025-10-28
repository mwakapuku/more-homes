from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'profile', 'otp')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'first_name', 'last_name', 'groups'),
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'phone', 'otp', 'otp_expiry',
        'max_otp_try', 'verified', 'is_superuser', 'is_staff', 'is_active', 'has_dept')
    list_filter = ('verified', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    ordering = ('id',)
    list_per_page = 20
    list_max_show_all = 100