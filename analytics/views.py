from rest_framework import generics
from .models import AgentPerformance, Feedback
from .serializers import AgentPerformanceSerializer, FeedbackSerializer

class AgentPerformanceListCreateView(generics.ListCreateAPIView):
    queryset = AgentPerformance.objects.all()
    serializer_class = AgentPerformanceSerializer

class FeedbackListCreateView(generics.ListCreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
