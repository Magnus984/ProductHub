from rest_framework.exceptions import APIException
from rest_framework import status

class ProductException(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail=detail)
        self.code = code

class ProductNotFound(ProductException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Product not found'
    default_code = 'product_not_found'


class CategoryNotFound(ProductException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Category not found'
    default_code = 'category_not_found'




class InvalidImageFormat(ProductException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid image format'
    default_code = 'invalid_image_format'


class InvalidPriceRange(ProductException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid price range'
    default_code = 'invalid_price_range'



class InvalidRating(ProductException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid rating'
    default_code = 'invalid_rating'
