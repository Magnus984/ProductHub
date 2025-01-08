from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from .models import Product, Category, Review
from .serializers import ProductSerializer, CategorySerializer, ReviewSerializer
from utils.pagination import CustomPagination
from .utils import handle_product_exceptions, validate_product, validate_category, validate_product_image, validate_product_price, validate_product_review

class ProductListCreateView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = CustomPagination

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

    @handle_product_exceptions
    def post(self, request):
        """Create a new product"""
        # Validate product data
        print("request.data", request.data)
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

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk)

    def get(self, request, pk):
        """Get a specific product with its reviews and categories"""
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

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

    def patch(self, request, pk):
        """Partially update a product"""
        return self.put(request, pk)

    def delete(self, request, pk):
        """Delete a product"""
        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductReviewView(APIView):
    pagination_class = CustomPagination

    def get(self, request, pk):
        """Get all reviews for a specific product"""
        product = get_object_or_404(Product, pk=pk)
        reviews = Review.objects.filter(product_id=product)
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_reviews = paginator.paginate_queryset(reviews, request)
        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)

    @handle_product_exceptions
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

    def get(self, request):
        """Get all categories"""
        categories = Category.objects.all()
        
        # Apply pagination
        paginator = self.pagination_class()
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = CategorySerializer(paginated_categories, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Create a new category"""
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class CategoryDetailView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Category, pk=pk)

    def get(self, request, pk):
        """Get a specific category"""
        category = self.get_object(pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a category"""
        category = self.get_object(pk)
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a category"""
        category = self.get_object(pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)