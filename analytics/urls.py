from django.urls import path
from .views import (
    AgentPerformanceListCreateView,
    AgentPerformanceLogListView,
    FeedbackListCreateView,
    AgentPerformanceAnalysisView,
    OperationsSummaryView,
    CXOptimizationView,
)

urlpatterns = [
    path('agent-performance/', AgentPerformanceListCreateView.as_view(), name='agent-performance-list-create'),
    path('agent-performance-logs/', AgentPerformanceLogListView.as_view(), name='agent-performance-log-list'),
    path('agent-performance-analysis/<str:agent_name>/', AgentPerformanceAnalysisView.as_view(), name='agent-performance-analysis'),
    path('feedback/', FeedbackListCreateView.as_view(), name='feedback-list-create'),
    path('operations-summary/<int:company_id>/', OperationsSummaryView.as_view(), name='operations-summary'),
    path('cx-optimization/<int:company_id>/', CXOptimizationView.as_view(), name='cx-optimization'),
]
