from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from accounts.models import User

class StartConversationView(generics.GenericAPIView):
    """POST /api/messaging/start/<user_id>/ - get or create a conversation with another user"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        other_user = get_object_or_404(User, id=user_id)
        # Find existing conversation where both are participants
        conv = Conversation.objects.filter(participants=request.user).filter(participants=other_user).distinct()
        if conv.exists():
            conv = conv.first()
        else:
            conv = Conversation.objects.create()
            conv.participants.add(request.user, other_user)
        serializer = ConversationSerializer(conv, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConversationListView(generics.ListAPIView):
    """GET /api/messaging/conversations/ - list all conversations for logged-in user"""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

class MessageListView(generics.ListCreateAPIView):
    """GET /api/messaging/conversations/<conv_id>/messages/ - list messages in a conversation
       POST - send a new message to that conversation"""
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        conv = get_object_or_404(Conversation, id=self.kwargs['conv_id'])
        if self.request.user not in conv.participants.all():
            return Message.objects.none()
        return conv.messages.all().order_by('created_at')

    def perform_create(self, serializer):
        conv = get_object_or_404(Conversation, id=self.kwargs['conv_id'])
        if self.request.user not in conv.participants.all():
            raise PermissionError("You are not a participant")
        serializer.save(conversation=conv, sender=self.request.user)

class MarkMessagesReadView(generics.GenericAPIView):
    """PATCH /api/messaging/conversations/<conv_id>/read/ - mark all unread messages as read (except sender)"""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, conv_id):
        conv = get_object_or_404(Conversation, id=conv_id)
        if request.user not in conv.participants.all():
            return Response({'error': 'Not a participant'}, status=403)
        unread_msgs = conv.messages.filter(is_read=False).exclude(sender=request.user)
        count = unread_msgs.update(is_read=True)
        return Response({'message': f'Marked {count} messages as read'})