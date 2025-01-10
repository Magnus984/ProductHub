# utils.py
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal, InvalidOperation

from .exceptions import (
    ProductException,
    ProductNotFound,
    CategoryNotFound,
    InvalidImageFormat,
    InvalidPriceRange,
    InvalidRating
)

from .models import Product, Category

def handle_product_exceptions(func):
    """
    Enhanced decorator to handle all product-related exceptions consistently
    Handles both custom product exceptions and standard Django/Python exceptions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # Custom product exceptions
        except ProductNotFound as e:
            return Response({'error': str(e)}, status=e.status_code)
        except CategoryNotFound as e:
            return Response({'error': str(e)}, status=e.status_code)
        except InvalidImageFormat as e:
            return Response({'error': str(e)}, status=e.status_code)
        except InvalidPriceRange as e:
            return Response({'error': str(e)}, status=e.status_code)
        except InvalidRating as e:
            return Response({'error': str(e)}, status=e.status_code)
        except ProductException as e:
            return Response({'error': str(e)}, status=e.status_code)
        # Django/Python exceptions
        except ObjectDoesNotExist as e:
            return Response(
                {'error': 'Requested resource not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except DatabaseError as e:
            # Log the database error here
            return Response(
                {'error': 'A database error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Log unexpected errors here
            return Response(
                {'error': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    return wrapper

def validate_product(product_id):
    """Validate product exists"""
    if not product_id:
        raise ProductException('Product ID is required')
    
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        raise ProductNotFound(f'Product with id {product_id} not found')

def validate_category(category_id):
    """Validate category exists"""
    if not category_id:
        raise ProductException('Category ID is required')
    
    try:
        category = Category.objects.get(id=category_id)
        return category
    except Category.DoesNotExist:
        raise CategoryNotFound(f'Category with id {category_id} not found')

def validate_product_image(image):
    """
    Validate product image format and size
    """
    if not image:
        return True  # Image is optional
    
    allowed_extensions = ['.jpg', '.jpeg', '.png']
    max_size = 5 * 1024 * 1024  # 5MB
    
    file_extension = image.name.lower()
    if not any(file_extension.endswith(ext) for ext in allowed_extensions):
        raise InvalidImageFormat(
            'Invalid image format. Allowed formats: JPG, JPEG, PNG'
        )
    
    if image.size > max_size:
        raise InvalidImageFormat('Image size must be less than 5MB')
    
    return True

def validate_product_price(price):
    """
    Validate product price
    """
    try:
        price = Decimal(str(price))
        if price <= 0:
            raise InvalidPriceRange('Price must be greater than 0')
        return price
    except (InvalidOperation, TypeError, ValueError):
        raise InvalidPriceRange('Invalid price format')

def validate_product_review(rating, comment):
    """
    Validate product review rating and comment
    """
    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise InvalidRating('Rating must be between 1 and 5')
    except (ValueError, TypeError):
        raise InvalidRating('Rating must be a valid number between 1 and 5')
    
    if not comment or len(comment.strip()) == 0:
        raise ProductException('Review comment is required')
    
    if len(comment) > 200:
        raise ProductException('Review comment must be less than 200 characters')
    
    return rating, comment
