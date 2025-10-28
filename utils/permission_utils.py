from rest_framework import permissions


class AddPermission(permissions.BasePermission):
    model = None

    def has_permission(self, request, view):
        if not self.model:
            return False
        perm = f"{self.model._meta.app_label}.add_{self.model._meta.model_name}"
        return request.user.has_perm(perm)


class ViewPermission(permissions.BasePermission):
    model = None

    def has_permission(self, request, view):
        if not self.model:
            return False
        perm = f"{self.model._meta.app_label}.view_{self.model._meta.model_name}"
        return request.user.has_perm(perm)


class ChangePermission(permissions.BasePermission):
    model = None

    def has_permission(self, request, view):
        if not self.model:
            return False
        perm = f"{self.model._meta.app_label}.change_{self.model._meta.model_name}"
        return request.user.has_perm(perm)


class DeletePermission(permissions.BasePermission):
    model = None

    def has_permission(self, request, view):
        if not self.model:
            return False
        perm = f"{self.model._meta.app_label}.delete_{self.model._meta.model_name}"
        return request.user.has_perm(perm)


class WebhookPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Only allow trusted IPs or API keys
        trusted_ip = "197.123.45.67"
        return request.META.get("REMOTE_ADDR") == trusted_ip
