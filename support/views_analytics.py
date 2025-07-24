from rest_framework import generics
from analytics.models import AgentPerformanceLog, Feedback
from analytics.serializers import AgentPerformanceLogSerializer, FeedbackSerializer

class AgentPerformanceLogListView(generics.ListAPIView):
    serializer_class = AgentPerformanceLogSerializer
    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return AgentPerformanceLog.objects.filter(ticket_id=ticket_id).order_by('created_at')
        return AgentPerformanceLog.objects.all().order_by('-created_at')

class FeedbackCreateView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()

class FeedbackListView(generics.ListAPIView):
    serializer_class = FeedbackSerializer
    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return Feedback.objects.filter(ticket_id=ticket_id).order_by('-created_at')
        return Feedback.objects.all().order_by('-created_at')
