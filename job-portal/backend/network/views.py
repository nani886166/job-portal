from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Follow
from profiles.serializers import UserBasicSerializer
from accounts.models import User

class FollowUserView(generics.GenericAPIView):
    """POST /api/network/follow/<user_id>/ - follow/unfollow toggle"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        target = get_object_or_404(User, id=user_id)
        if target == request.user:
            return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

        follow_obj, created = Follow.objects.get_or_create(follower=request.user, following=target)
        if not created:
            follow_obj.delete()
            return Response({'followed': False, 'message': 'Unfollowed'}, status=status.HTTP_200_OK)
        return Response({'followed': True, 'message': 'Followed'}, status=status.HTTP_201_CREATED)

class MyFollowersView(generics.ListAPIView):
    """GET /api/network/my/followers/ - list of users who follow me"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(following_set__following=self.request.user)

class MyFollowingView(generics.ListAPIView):
    """GET /api/network/my/following/ - list of users I follow"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(followers_set__follower=self.request.user)

class UserFollowersView(generics.ListAPIView):
    """GET /api/network/users/<user_id>/followers/ - public list of a user's followers"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        return User.objects.filter(followers_set__follower=user)

class UserFollowingView(generics.ListAPIView):
    """GET /api/network/users/<user_id>/following/ - public list of users a user follows"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        user = get_object_or_404(User, id=self.kwargs['user_id'])
        return User.objects.filter(following_set__following=user)

class SearchUsersView(generics.ListAPIView):
    """GET /api/network/search/?q=... - search users (by name, email) excluding self"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('p', '').strip()
        if not query:
            return User.objects.none()
        return User.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=self.request.user.id)
        

class SuggestedUsersView(generics.ListAPIView):
    """GET /api/network/suggested/ - users you may know (people you don't follow)"""
    serializer_class = UserBasicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        following_ids = Follow.objects.filter(follower=self.request.user).values_list('following_id', flat=True)
        return User.objects.exclude(id=self.request.user.id).exclude(id__in=following_ids)[:50]

class FollowStatusView(generics.GenericAPIView):
    """GET /api/network/follow-status/?user_ids=1,2,3 - batch check if current user follows these users"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_ids = request.query_params.get('user_ids', '')
        if not user_ids:
            return Response({})
        ids = [int(i) for i in user_ids.split(',') if i.isdigit()]
        followed_ids = set(Follow.objects.filter(follower=request.user, following_id__in=ids).values_list('following_id', flat=True))
        return Response({str(uid): (uid in followed_ids) for uid in ids})
