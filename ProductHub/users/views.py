from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from .models import CustomUser, Customer, Admin
from .serializers import CustomUserSerializer, CustomerSerializer, AdminSerializer
from django.utils.decorators import method_decorator

User = get_user_model()

class RegisterCustomerView(APIView):
    """Register customer view."""
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Customer registered successfully'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RegisterAdminView(APIView):
    """Register admin view."""
    def post(self, request):
        serializer = AdminSerializer(data=request.data)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Admin registered successfully'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCurrentUserView(APIView):
    """Get current logged-in user view.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
