from django.urls import path
from .views import AgentPerformanceListCreateView, FeedbackListCreateView

urlpatterns = [
    path('agent-performance/', AgentPerformanceListCreateView.as_view(), name='agent-performance-list-create'),
    path('feedback/', FeedbackListCreateView.as_view(), name='feedback-list-create'),
]
