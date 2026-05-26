from django.urls import path
from .views import ProfileView, UserProfileView

urlpatterns = [
    path('me/', ProfileView.as_view(), name='my-profile'),                     # /api/profiles/me/
    path('user/<int:user_id>/', UserProfileView.as_view(), name='user-profile'), # /api/profiles/user/1/
]