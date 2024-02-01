from rest_framework.permissions import BasePermission


class SuperAdminPermission(BasePermission):
    message = "super admin "

    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser is True:
            return True
        return False
