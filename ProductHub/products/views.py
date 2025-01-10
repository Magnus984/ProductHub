from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from utils.pagination import CustomPagination
from users.permissions import IsAdmin, IsCustomer
from rest_framework.permissions import IsAuthenticated
from .utils import validate_product_image, validate_product_price, validate_category, validate_product, validate_product_review
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductListCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAdmin]
        return super().get_permissions()

    @swagger_auto_schema(
        operation_description="Get all products",
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search term", type=openapi.TYPE_STRING),
            openapi.Parameter('category', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('min_price', openapi.IN_QUERY, description="Minimum price", type=openapi.TYPE_NUMBER, format='float'),
            openapi.Parameter('max_price', openapi.IN_QUERY, description="Maximum price", type=openapi.TYPE_NUMBER, format='float'),
            openapi.Parameter('sort', openapi.IN_QUERY, description="Sort order", type=openapi.TYPE_STRING)
        ]
    )
    def get(self, request):
        """Get all products with filtering, sorting, and search"""
        queryset = Product.objects.all()

        # Search
        search_query = request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Category Filter
        category_id = request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(categories__id=category_id)

        # Price Filter
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        # Rating Filter
        min_rating = request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating'))\
                              .filter(avg_rating__gte=min_rating)

        # Sorting
        sort_by = request.query_params.get('sort')
        if sort_by:
            sort_mapping = {
                'price_asc': 'price',
                'price_desc': '-price',
                'name_asc': 'name',
                'name_desc': '-name',
                'rating': '-avg_rating'
            }
            sort_field = sort_mapping.get(sort_by)
            if sort_field:
                queryset = queryset.order_by(sort_field)

        # Apply pagination
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new product",
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_FORM, description="Name", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('description', openapi.IN_FORM, description="Description", type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('price', openapi.IN_FORM, description="Price", type=openapi.TYPE_NUMBER, format='float', required=True),
            openapi.Parameter('image', openapi.IN_FORM, description="Image", type=openapi.TYPE_FILE, required=True),
            openapi.Parameter('categories', openapi.IN_FORM, description="Categories", type=openapi.TYPE_STRING, required=True)
        ]
    )
    def post(self, request):
        """Create a new product"""
        # Validate product data
        validate_product_image(request.FILES.get('image'))


        price = validate_product_price(request.data.get('price'))

        serializer = ProductSerializer(data=request.data)


        serializer.is_valid(raise_exception=True)
        product = serializer.save()


        category_ids = request.data.get('category_ids', [])
        if category_ids:
            for category_id in category_ids:
                validate_category(category_id)
            product.categories.set(category_ids)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
        

class ProductDetailView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsCustomer | IsAdmin]
        return super().get_permissions()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsCustomer, IsAdmin]
        return super().get_permissions()

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    @swagger_auto_schema(
        operation_description="Get product details",
        tags=["Products"]
    )
    def get(self, request, pk):
        """Get a specific product with its reviews and categories"""
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a product",
        tags=["Products"],
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_FORM, description="Name", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('description', openapi.IN_FORM, description="Description", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('price', openapi.IN_FORM, description="Price", type=openapi.TYPE_NUMBER, format='float', required=False),
            openapi.Parameter('image', openapi.IN_FORM, description="Image", type=openapi.TYPE_FILE, required=False),
            openapi.Parameter('categories', openapi.IN_FORM, description="Categories", type=openapi.TYPE_STRING, required=False)
        ]
    )
    def put(self, request, pk):
        """Update a product"""
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_product = serializer.save()
            
            # Handle categories update if provided
            category_ids = request.data.get('category_ids')
            if category_ids is not None:
                updated_product.categories.set(category_ids)
            
            return Response(ProductSerializer(updated_product).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Partially update a product",
        tags=["Products"]
    )
    def patch(self, request, pk):
        """Partially update a product"""
        return self.put(request, pk)

    @swagger_auto_schema(
        operation_description="Delete a product",
        tags=["Products"]
    )
    def delete(self, request, pk):
        """Delete a product"""
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductReviewView(APIView):
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated, IsCustomer]

    @swagger_auto_schema(
        operation_description="Get all reviews for a specific product",
        tags=["Reviews"]
    )
    def get(self, request, pk):
        """Get all reviews for a specific product"""
        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product_id=product)
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Add a review to a product",
        tags=["Reviews"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'rating': openapi.Schema(type=openapi.TYPE_INTEGER, description='Rating'),
                'comment': openapi.Schema(type=openapi.TYPE_STRING, description='Comment')
            }
        )
    )
    def post(self, request, pk):
        """Add a review to a product"""
        product = validate_product(pk)
        
        validate_product_review(
            request.data.get('rating'),
            request.data.get('comment')
        )
        serializer = ReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(product_id=product)



        return Response(serializer.data, status=status.HTTP_201_CREATED)
        
class CategoryListCreateView(APIView):
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsAdmin]
        return super().get_permissions()
    
    @swagger_auto_schema(
        operation_description="Get all categories",
        tags=["Categories"]
    )
    def get(self, request):
        """Get all categories"""
        categories = Category.objects.all()
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="Create a new category",
        tags=["Categories"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description')
            }
        )
    )
    def post(self, request):
        """Create a new category"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CategoryDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['PUT', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated, IsCustomer]
        return super().get_permissions()

    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    @swagger_auto_schema(
        operation_description="Get a specific category",
        tags=["Categories"]
    )
    def get(self, request, pk):
        """Get a specific category"""
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update a category",
        tags=["Categories"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Name'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Description')
            }
        )
    )
    def put(self, request, pk):
        """Update a category"""
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Delete a category",
        tags=["Categories"]
    )
    def delete(self, request, pk):
        """Delete a category"""
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)