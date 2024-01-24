from django.urls import path
from .views import Chat, ChatReset, ChatUpload, ChatState, Visit

app_name = "chatbot"

urlpatterns = [
    path("chat/", Chat.as_view(), name="main"),
    path("reset", ChatReset.as_view(), name="reset"),
    path("upload", ChatUpload.as_view(), name="upload"),
    path("state", ChatState.as_view(), name="state"),
    path('visit', Visit.as_view(), name='visit')
]
