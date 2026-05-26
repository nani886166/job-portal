from django.urls import path
from .views import (
    StartConversationView,
    ConversationListView,
    MessageListView,
    MarkMessagesReadView,
)

urlpatterns = [
    path('start/<int:user_id>/', StartConversationView.as_view(), name='start-conversation'),
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:conv_id>/messages/', MessageListView.as_view(), name='message-list'),
    path('conversations/<int:conv_id>/read/', MarkMessagesReadView.as_view(), name='mark-read'),
]