from django.urls import path
from .views import CompanyListCreate, CompanyDetail, TicketListCreate, TicketDetail, FileUploadView, ChatbotInteractionView

urlpatterns = [
    path('companies/', CompanyListCreate.as_view(), name='company-list-create'),
    path('companies/<int:pk>/', CompanyDetail.as_view(), name='company-detail'),
    path('tickets/', TicketListCreate.as_view(), name='ticket-list-create'),
    path('tickets/<int:pk>/', TicketDetail.as_view(), name='ticket-detail'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('chatbot/', ChatbotInteractionView.as_view(), name='chatbot-interaction'),
]

