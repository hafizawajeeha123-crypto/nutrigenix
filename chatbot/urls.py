from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chatbot/',            views.chatbot_view, name='chatbot'),
    path('api/chat/',           views.chat_api,     name='chat_api'),
    path('api/chat/clear/',     views.clear_chat,   name='clear_chat'),
]