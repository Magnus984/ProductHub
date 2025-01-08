from rest_framework.exceptions import APIException
from rest_framework import status

class CartException(APIException):
    """Base exception for cart-related errors"""
    default_detail = 'An error occurred while processing your cart'
    default_code = 'cart_error'

class CartItemNotFoundException(CartException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Cart item not found'
    default_code = 'cart_item_not_found'

class InvalidQuantityException(CartException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid quantity provided'
    default_code = 'invalid_quantity'

class ProductNotFoundException(CartException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Product not found'
    default_code = 'product_not_found'
