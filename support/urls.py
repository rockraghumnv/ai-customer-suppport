from django.urls import path
from .views import CompanyListCreate, CompanyDetail, TicketListCreate, TicketDetail, FileUploadView, ChatbotInteractionView, ProductListCreate, ProductDetail, ServiceListCreate, ServiceDetail, ChatMessageListView, CopilotSummaryView, UserRegisterView, UserLoginView, FeedbackView, FeedbackListView, AgentPerformanceView, CXOptimizationView, UploadedFileListView, UploadedFileDetailView

urlpatterns = [
    path('companies/', CompanyListCreate.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', CompanyDetail.as_view(), name='company-detail'),
    path('tickets/', TicketListCreate.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetail.as_view(), name='ticket-detail'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('chatbot/', ChatbotInteractionView.as_view(), name='chatbot-interaction'),
    path('products/', ProductListCreate.as_view(), name='product-list-create'),
    path('products/<int:pk>/', ProductDetail.as_view(), name='product-detail'),
    path('services/', ServiceListCreate.as_view(), name='service-list-create'),
    path('services/<int:pk>/', ServiceDetail.as_view(), name='service-detail'),
    path('chat-messages/', ChatMessageListView.as_view(), name='chat-message-list'),
    path('copilot-summary/<int:ticket_id>/', CopilotSummaryView.as_view(), name='copilot-summary'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('feedback/', FeedbackView.as_view(), name='feedback'),
    path('feedback-list/', FeedbackListView.as_view(), name='feedback-list'),
    path('agent-performance/', AgentPerformanceView.as_view(), name='agent-performance'),
    path('cx-analytics/', CXOptimizationView.as_view(), name='cx-analytics'),
    path('uploaded-files/', UploadedFileListView.as_view(), name='uploadedfile-list'),
    path('uploaded-files/<int:pk>/', UploadedFileDetailView.as_view(), name='uploadedfile-detail'),
]

