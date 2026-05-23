from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain_google_genai import GoogleGenerativeAI
from .models import Ticket
from .serializers import TicketSerializer

class TicketListCreateView(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class TicketDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class TicketAutomationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        description = request.data.get('description')
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = (
            "Categorize, prioritize, and suggest incident links for this ticket description:\n"
            f"{description}"
        )
        result = gemini.generate(prompt)
        return Response({'automation': result})
