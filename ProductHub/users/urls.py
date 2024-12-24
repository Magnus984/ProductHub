from django.urls import path
from .views import RegisterAdminView, RegisterCustomerView, LoginView, LogoutView, GetCurrentUserView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-customer/', RegisterCustomerView.as_view(), name='register-customer'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('current-user/', GetCurrentUserView.as_view(), name='current-user'),
]