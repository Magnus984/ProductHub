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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()

class RegisterCustomerView(APIView):
    """Register customer view."""
    @swagger_auto_schema(
        operation_description="Registers a customer",
        tags=['Users'],
        responses={200: CustomerSerializer},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                "firstname": openapi.Schema(type=openapi.TYPE_STRING, description="Firstname"),
                "lastname": openapi.Schema(type=openapi.TYPE_STRING, description="Lastname"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                "residential_address": openapi.Schema(type=openapi.TYPE_STRING, description="residential_address"),
            }
            )
    )
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
    @swagger_auto_schema(
        operation_description="Registers an admin",
        tags=['Users'],
        responses={200: AdminSerializer},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                "firstname": openapi.Schema(type=openapi.TYPE_STRING, description="Firstname"),
                "lastname": openapi.Schema(type=openapi.TYPE_STRING, description="Lastname"),
                "password": openapi.Schema(type=openapi.TYPE_STRING, description="Password"),
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
            }
            )
    )
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

    @swagger_auto_schema(
        operation_description="Gets current logged-in user",
        tags=['Users']
    )
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
