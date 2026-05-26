from django.urls import path
from .views import (
    FollowUserView, MyFollowersView, MyFollowingView,
    UserFollowersView, UserFollowingView, SearchUsersView,
    SuggestedUsersView, FollowStatusView
)

urlpatterns = [
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow-user'),
    path('my/followers/', MyFollowersView.as_view(), name='my-followers'),
    path('my/following/', MyFollowingView.as_view(), name='my-following'),
    path('users/<int:user_id>/followers/', UserFollowersView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following/', UserFollowingView.as_view(), name='user-following'),
    path('search/', SearchUsersView.as_view(), name='search-users'),
    path('suggested/', SuggestedUsersView.as_view(), name='suggested-users'),
    path('follow-status/', FollowStatusView.as_view(), name='follow-status'),
]