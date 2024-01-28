from django.urls import path
from .views import ChatReset, ChatUpload, ChatState, Visit, ConversationCreate, ConversationDetail, ConversationFavourite, MessageList, MessageCreate, ConversationList

app_name = "chatbot"

urlpatterns = [
    # path("chat/", Chat.as_view(), name="main"),
    path("reset", ChatReset.as_view(), name="reset"),
    path("upload", ChatUpload.as_view(), name="upload"),
    path("state", ChatState.as_view(), name="state"),
    path('visit', Visit.as_view(), name='visit'),
    
    # Post for a conversation
    path('conversations/', ConversationCreate.as_view(), name='conversation-create'),
    # Get for all conversations
    path('conversations/list/', ConversationList.as_view(), name='conversation-list'),
    # Get, Put, Patch, Delete for a single conversation
    path('conversations/<int:pk>/', ConversationDetail.as_view(), name='conversation-detail'),
    # Post for favourite/unfavourite a conversation
    path('conversations/<int:pk>/favourite/', ConversationFavourite.as_view(), name='conversation-favourite'),
    # Get, Post for messages
    path('conversations/<int:conversation_id>/messages/', MessageList.as_view(), name='message-list'),
    # Post for creating a message
    path('conversations/<int:conversation_id>/messages/create/', MessageCreate.as_view(), name='message-create'),

]
