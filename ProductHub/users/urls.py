from django.urls import path
from .views import RegisterAdminView, RegisterCustomerView, GetCurrentUserView

urlpatterns = [
    path('register-customer/', RegisterCustomerView.as_view(), name='register-customer'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('current-user/', GetCurrentUserView.as_view(), name='current-user'),
]