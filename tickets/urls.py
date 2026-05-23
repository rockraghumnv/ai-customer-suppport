from django.urls import path
from .views import TicketListCreateView, TicketDetailView, TicketAutomationView

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('automation/', TicketAutomationView.as_view(), name='ticket-automation'),
]
