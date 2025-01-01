from rest_framework import serializers
from .models import CustomUser, Customer, Admin

class CustomUserSerializer(serializers.ModelSerializer):
    """Serializer for CustomUser model.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'residential_address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'email', 'residential_address']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """Validate username.
        """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Validate email.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        """create user.
        """
        user = CustomUser.objects.create_user(**validated_data)
        customer = Customer.objects.create(user=user, is_customer=True)
        return user


class AdminSerializer(serializers.ModelSerializer):
    """Serializer for Admin model.
    """
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'first_name', 'last_name', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """Validate username.
        """
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        """Validate email.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        """create user.
        """
        user = CustomUser.objects.create_user(**validated_data, is_admin=True)
        admin = Admin.objects.create(user=user)
        return user