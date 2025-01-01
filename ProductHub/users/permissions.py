from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Check if user is an admin.
    """
    def has_permission(self, request, view):
        return request.user.is_admin

class IsCustomer(BasePermission):
    """Check if user is a customer.
    """
    def has_permission(self, request, view):
        return request.user.is_customer