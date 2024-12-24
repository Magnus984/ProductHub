from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login, logout, authenticate
from .models import CustomUser, Customer, Admin
from .serializers import CustomUserSerializer, CustomerSerializer, AdminSerializer
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class RegisterCustomerView(APIView):
    """Register customer view.
    """
    def post(self, request):
        try:
            serializer = CustomerSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Customer created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Customer not registered: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterAdminView(APIView):
    """Register admin view.
    """
    def post(self, request):
        try:
            serializer = AdminSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Admin user created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': f'Admin not registered: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """Login view.
    """
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response({'message': 'User logged in successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'User not logged in: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout view.
    """
    def post(self, request):
        try:
            logout(request)
            return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': f'User not logged out: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)