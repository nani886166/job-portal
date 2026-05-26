from django.urls import path
from .views import RegisterView, LoginView, ForgotPasswordView, ResetPasswordView, UserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('me/', UserView.as_view(), name='me'),  # Endpoint to get current user info
]
