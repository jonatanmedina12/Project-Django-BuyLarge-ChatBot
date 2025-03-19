# chatbot/urls.py
from django.urls import path
from .views import ChatbotAPIView, ConversationHistoryView

urlpatterns = [
    path('', ChatbotAPIView.as_view(), name='chatbot-api'),
    path('conversations/<str:session_id>/', ConversationHistoryView.as_view(), name='conversation-history'),
]