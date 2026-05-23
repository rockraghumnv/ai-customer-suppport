from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain_google_genai import GoogleGenerativeAI
from chat.models import ChatMessage
from tickets.models import Ticket
from .models import AgentPerformance, Feedback, AgentPerformanceLog
from .serializers import AgentPerformanceSerializer, FeedbackSerializer, AgentPerformanceLogSerializer


class AgentPerformanceListCreateView(generics.ListCreateAPIView):
    queryset = AgentPerformance.objects.all()
    serializer_class = AgentPerformanceSerializer


class AgentPerformanceLogListView(generics.ListAPIView):
    serializer_class = AgentPerformanceLogSerializer

    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return AgentPerformanceLog.objects.filter(ticket_id=ticket_id).order_by('-created_at')
        return AgentPerformanceLog.objects.all().order_by('-created_at')


class FeedbackListCreateView(generics.ListCreateAPIView):
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return Feedback.objects.filter(ticket_id=ticket_id).order_by('-created_at')
        return Feedback.objects.all().order_by('-created_at')


class AgentPerformanceAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, agent_name):
        logs = AgentPerformanceLog.objects.filter(agent_name=agent_name).order_by('created_at')
        transcript = '\n'.join([f"{log.action}: {log.details}" for log in logs])
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = (
            "Analyze the following agent transcript for politeness, effectiveness, and suggest improvements.\n"
            f"{transcript}"
        )
        analysis = gemini.generate(prompt)
        return Response({'performance_analysis': analysis})


class OperationsSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        tickets = Ticket.objects.filter(company_id=company_id)
        summary = (
            f"Total tickets: {tickets.count()}\n"
            f"Open: {tickets.filter(status='open').count()}\n"
            f"Closed: {tickets.filter(status='closed').count()}"
        )
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Summarize support operations and trends for the following ticket data:\n{summary}"
        ai_summary = gemini.generate(prompt)
        return Response({'summary': ai_summary, 'raw': summary})


class CXOptimizationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        messages = ChatMessage.objects.filter(ticket__company_id=company_id)
        transcript = '\n'.join([m.message for m in messages if m.message])
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = (
            "Analyze customer sentiment, root causes of issues, and suggest proactive support actions for this transcript:\n"
            f"{transcript}"
        )
        result = gemini.generate(prompt)
        return Response({'cx_optimization': result})
