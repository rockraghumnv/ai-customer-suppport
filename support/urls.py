from django.urls import path
#from companies.views import CompanyListCreate, CompanyDetail
from .views_ticket import TicketListCreate, TicketDetail
from .views_knowledge import FileUploadView, ProductListCreate, ProductDetail, ServiceListCreate, ServiceDetail
from .views_chat import ChatMessageListView, ChatbotInteractionView, CopilotSummaryView
from .views_analytics import AgentPerformanceLogListView, FeedbackCreateView, FeedbackListView

urlpatterns = [
    # path('companies/', CompanyListCreate.as_view(), name='company-list-create'),
    # path('companies/<int:pk>/', CompanyDetail.as_view(), name='company-detail'),
    path('tickets/', TicketListCreate.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetail.as_view(), name='ticket-detail'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('services/', ServiceListCreate.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('chat-messages/', ChatMessageListView.as_view(), name='chat-message-list'),
    path('chatbot/', ChatbotInteractionView.as_view(), name='chatbot-interaction'),
    path('copilot-summary/<int:ticket_id>/', CopilotSummaryView.as_view(), name='copilot-summary'),
    path('agent-performance/', AgentPerformanceLogListView.as_view(), name='agent-performance-list'),
    path('feedback/', FeedbackCreateView.as_view(), name='feedback-create'),
    path('feedback-list/', FeedbackListView.as_view(), name='feedback-list'),
]

