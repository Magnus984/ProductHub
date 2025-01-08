# utils.py
from functools import wraps
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from rest_framework.response import Response
from rest_framework import status
from .exceptions import (
    CartException,
    CartItemNotFoundException,
    InvalidQuantityException,
    ProductNotFoundException
)

from products.models import Product

def handle_cart_exceptions(func):
    """
    Enhanced decorator to handle all cart-related exceptions consistently
    Handles both custom cart exceptions and standard Django/Python exceptions
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        # Custom cart exceptions
        except CartItemNotFoundException as e:
            return Response({'error': str(e)}, status=e.status_code)
        except InvalidQuantityException as e:
            return Response({'error': str(e)}, status=e.status_code)
        except ProductNotFoundException as e:
            return Response({'error': str(e)}, status=e.status_code)
        except CartException as e:
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
    """Validate product exists and is active"""
    if not product_id:
        raise CartException('Product ID is required')
    
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        raise ProductNotFoundException(f'Product with id {product_id} not found')


def validate_cart_item_quantity(quantity, raise_exception=True):
    """
    Validate cart item quantity
    Args:
        quantity: The quantity to validate
        raise_exception: Whether to raise an exception or return False
    """
    try:
        quantity = int(quantity)
        if quantity <= 0:
            if raise_exception:
                raise InvalidQuantityException('Quantity must be greater than 0')
            return False
        return quantity
    except (ValueError, TypeError):
        if raise_exception:
            raise InvalidQuantityException('Quantity must be a valid number')
        return False