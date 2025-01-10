"""URL configuration for ProductHub project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt import views as jwt_views
from rest_framework import permissions
<<<<<<< HEAD

from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Product Hub API",
        default_version='v1',
        description="My API description",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="amglna2020@gmail.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)
=======
from drf_yasg.views import get_schema_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="ProductHub API",
      default_version='v1',
      description="Product hub is an e-commerce-like application programming interface.",
      terms_of_service="https://www.google.com/policies/terms/",
      #contact=openapi.Contact(email="contact@snippets.local"),
      #license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
   authentication_classes=[]
)

class CustomTokenObtainPairView(jwt_views.TokenObtainPairView):
    @swagger_auto_schema(tags=['Auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class CustomTokenRefreshView(jwt_views.TokenRefreshView):
    @swagger_auto_schema(tags=['Auth'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

>>>>>>> a7205d9e0fdc428f0d172764d638867e3797ea1e

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
<<<<<<< HEAD
    path('api/products/', include('products.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
=======
    path('api/v1/',
        include([
            path('products/', include('products.urls')),
            path('cart/', include('cart.urls')),
            path('orders/', include('orders.urls')),
            path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
            path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
        ])
        ),
>>>>>>> a7205d9e0fdc428f0d172764d638867e3797ea1e
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)