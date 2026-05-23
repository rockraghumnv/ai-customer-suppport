from django.urls import path
from .views import ChatbotInteractionView, CopilotSummaryView

urlpatterns = [
    path('chatbot/', ChatbotInteractionView.as_view(), name='chatbot-interaction'),
    path('copilot-summary/<int:ticket_id>/', CopilotSummaryView.as_view(), name='copilot-summary'),
]

