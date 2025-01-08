from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework import status

class IsAdmin(BasePermission):
    """Check if user is an admin.
    """
    def has_permission(self, request, view):
        try:
            return request.user.is_admin
        except AttributeError:
            return Response({'error': 'User is not an admin'}, status=status.HTTP_403_FORBIDDEN)

class IsCustomer(BasePermission):
    """Check if user is a customer.
    """
    def has_permission(self, request, view):
        try:
            return request.user.is_customer
        except AttributeError:
            return Response({'error': 'User is not a customer'}, status=status.HTTP_403_FORBIDDEN)  