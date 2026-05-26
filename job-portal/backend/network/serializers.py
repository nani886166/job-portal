from rest_framework import serializers
from .models import Follow
from profiles.serializers import UserBasicSerializer   # we'll add this below

class FollowSerializer(serializers.ModelSerializer):
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)

    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']