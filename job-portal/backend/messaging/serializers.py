from rest_framework import serializers
from .models import Conversation, Message
from profiles.serializers import UserBasicSerializer   # reuse existing

class MessageSerializer(serializers.ModelSerializer):
    sender_info = UserBasicSerializer(source='sender', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'sender_info', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'conversation', 'sender', 'created_at', 'is_read']

class ConversationSerializer(serializers.ModelSerializer):
    participants_info = UserBasicSerializer(source='participants', many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'participants_info', 'last_message', 'unread_count', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        return MessageSerializer(msg).data if msg else None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0