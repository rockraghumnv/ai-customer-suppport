from django.shortcuts import render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from companies.models import Company
from tickets.models import Ticket 
from knowledge_base.models import UploadedFile
from .serializers import CompanySerializer, TicketSerializer, UploadedFileSerializer
# Import helper functions for ChromaDB integration (will implement next)
from .agents.chroma_utils import process_file_for_chroma
from rest_framework.views import APIView
# Import the agent router function (will implement next)
from .agents.agent_router import route_query_to_agent

class CompanyListCreate(generics.ListCreateAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class CompanyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

class TicketListCreate(generics.ListCreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class TicketDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

class FileUploadView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UploadedFileSerializer

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company')
        uploaded_file = request.data.get('file')

        if not company_id or not uploaded_file:
            return Response({'error': 'Company ID and file are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create and save the UploadedFile instance
        file_serializer = self.get_serializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        uploaded_file_instance = file_serializer.save(company=company) # Link file to company

        # Process the file for ChromaDB (implement this function in chroma_utils.py)
        try:
            process_file_for_chroma(uploaded_file_instance)
        except Exception as e:
            # Log the error and potentially inform the user
            print(f"Error processing file for ChromaDB: {e}")
            # You might want to delete the uploaded file instance if processing fails
            # uploaded_file_instance.delete()
            return Response({'error': f'File uploaded but failed to process for knowledge base: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(file_serializer.data, status=status.HTTP_201_CREATED)

class ChatbotInteractionView(APIView):
    """Handles customer-facing chatbot interactions."""
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')
        company_identifier = request.data.get('company')
        user_email = request.data.get('user_email') # Get user email

        if not query or not company_identifier or not user_email:
            return Response({'error': 'Query, company identifier, and user email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Assuming company_identifier is the company domain for now
            company = Company.objects.get(domain=company_identifier)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Route the query to the appropriate AI agent
        try:
            agent_response = route_query_to_agent(query, company, user_email) # Pass user_email

            # Check if the response is a ticket object (fallback case)
            if isinstance(agent_response, Ticket):
                ticket_serializer = TicketSerializer(agent_response)
                return Response({'message': 'I couldn\'t find an immediate answer. A support ticket has been created for you.', 'ticket': ticket_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                # Otherwise, it's a direct response from an agent
                return Response({'response': agent_response}, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the error
            print(f"Error routing query to agent: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
