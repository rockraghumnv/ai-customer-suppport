from django.shortcuts import render
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
# HEAD version: use modular imports for models and only necessary serializers
from companies.models import Company
from tickets.models import Ticket
from knowledge_base.models import UploadedFile
from .serializers import CompanySerializer, TicketSerializer, UploadedFileSerializer
# Import helper functions for ChromaDB integration (will implement next)
from .agents.chroma_utils import process_file_for_chroma
from rest_framework.views import APIView
# Import the agent router function (will implement next)
from .agents.agent_router import route_query_to_agent
from .agents.copilot_agent import CopilotAgent
from PIL import Image
import io
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination
from langchain_google_genai import GoogleGenerativeAI
import pytesseract

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

        # File type validation
        allowed_types = [
            'text/plain', 'application/pdf', 'application/json',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/gif', 'image/webp'
        ]
        if uploaded_file.content_type not in allowed_types:
            return Response({'error': f'Unsupported file type: {uploaded_file.content_type}'}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded_file.size > 10 * 1024 * 1024:  # 10MB limit
            return Response({'error': 'File too large (max 10MB).'}, status=status.HTTP_400_BAD_REQUEST)

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

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return ChatMessage.objects.filter(ticket_id=ticket_id).order_by('created_at')
        return ChatMessage.objects.none()

class ChatbotInteractionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    """Handles customer-facing chatbot interactions with optional image upload and persistent chat memory."""
    def post(self, request, *args, **kwargs):
        query = request.data.get('query')
        company_identifier = request.data.get('company')
        user_email = request.data.get('user_email')
        image_file = request.FILES.get('image')

        if not query or not company_identifier or not user_email:
            return Response({'error': 'Query, company identifier, and user email are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(domain=company_identifier)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        extracted_text = ''
        uploaded_file_instance = None
        chat_image = None
        if image_file:
            uploaded_file_instance = UploadedFile.objects.create(company=company, file=image_file)
            chat_image = uploaded_file_instance.file
            try:
                image = Image.open(chat_image)
                extracted_text = pytesseract.image_to_string(image)
            except Exception as e:
                extracted_text = "[Image uploaded, but OCR failed]"

        # Save user message
        user_msg = ChatMessage.objects.create(
            company=company,
            user_email=user_email,
            sender='user',
            message=query,
            image=chat_image
        )

        # Combine query and extracted text
        full_query = query
        if extracted_text:
            full_query = f"{query}\n\nImage context: {extracted_text}"

        try:
            agent_response = route_query_to_agent(full_query, company, user_email)
            if isinstance(agent_response, Ticket):
                if uploaded_file_instance:
                    uploaded_file_instance.ticket = agent_response
                    uploaded_file_instance.save()
                # Save fallback agent message
                ChatMessage.objects.create(
                    ticket=agent_response,
                    company=company,
                    user_email=user_email,
                    sender='agent',
                    message='A support ticket has been created for you. Our team will assist you shortly.'
                )
                ticket_serializer = TicketSerializer(agent_response)
                return Response({'message': 'I couldn\'t find an immediate answer. A support ticket has been created for you.', 'ticket': ticket_serializer.data}, status=status.HTTP_201_CREATED)
            else:
                # Save agent response
                ChatMessage.objects.create(
                    company=company,
                    user_email=user_email,
                    sender='agent',
                    message=str(agent_response)
                )
                return Response({'response': agent_response}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error routing query to agent: {e}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# --- User Feedback (CX Analytics) ---
from rest_framework import serializers
class FeedbackSerializer(serializers.Serializer):
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all())
    user_email = serializers.EmailField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True)

class FeedbackView(APIView):
    def post(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            Feedback.objects.create(**serializer.validated_data)
            return Response({'status': 'Feedback submitted'})
        return Response(serializer.errors, status=400)

class FeedbackListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        feedbacks = Feedback.objects.all().order_by('-created_at')
        paginator = PageNumberPagination()
        paginated_feedbacks = paginator.paginate_queryset(feedbacks, request)
        data = [
            {
                'company': f.company.id,
                'user_email': f.user_email,
                'rating': f.rating,
                'comment': f.comment,
                'created_at': f.created_at
            } for f in paginated_feedbacks
        ]
        return paginator.get_paginated_response(data)

class ProductListCreate(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ServiceListCreate(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class ServiceDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class CopilotSummaryView(APIView):
    """Returns a summary and suggested actions for a ticket for human agents, with full chat context."""
    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        # Gather all chat messages for this ticket
        chat_history = ChatMessage.objects.filter(ticket=ticket).order_by('created_at')
        conversation = '\n'.join([f"{msg.sender}: {msg.message}" for msg in chat_history])
        # Use Gemini to summarize and suggest
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Summarize the following support conversation and suggest next actions for the agent.\n\n{conversation}"
        summary = gemini.generate([prompt])
        return Response({'summary': summary, 'conversation': conversation}, status=status.HTTP_200_OK)

# --- User Registration & Login (Demo) ---
class UserRegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            return Response({'error': 'Username and password required.'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists.'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class UserLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid credentials.'}, status=400)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

# --- Company Config: FAQs, Guides, Policies (Demo, minimal) ---
class CompanyFAQView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, company_id):
        faq = request.data.get('faq')
        company = Company.objects.get(id=company_id)
        if not hasattr(company, 'faqs'):
            company.faqs = []
        company.faqs.append(faq)
        company.save()
        return Response({'faqs': company.faqs})
    def get(self, request, company_id):
        company = Company.objects.get(id=company_id)
        return Response({'faqs': getattr(company, 'faqs', [])})

# --- Agent Performance Monitoring (Demo) ---
class AgentPerformanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, agent_username):
        # Collect all chat messages for this agent
        messages = ChatMessage.objects.filter(user_email=agent_username, sender='agent')
        transcript = '\n'.join([m.message for m in messages])
        # Use Gemini to analyze
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Analyze the following agent transcript for politeness, effectiveness, and suggest improvements.\n{transcript}"
        analysis = gemini.generate(prompt)
        return Response({'performance_analysis': analysis})

# --- Operations Summary & Reporting (Demo) ---
class OperationsSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, company_id):
        tickets = Ticket.objects.filter(company_id=company_id)
        summary = f"Total tickets: {tickets.count()}\nOpen: {tickets.filter(status='open').count()}\nClosed: {tickets.filter(status='closed').count()}"
        # Use Gemini for trends
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Summarize support operations and trends for the following ticket data:\n{summary}"
        ai_summary = gemini.generate(prompt)
        return Response({'summary': ai_summary, 'raw': summary})

# --- CX Optimizations: Sentiment, Root Cause, Proactive (Demo) ---
class CXOptimizationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, company_id):
        messages = ChatMessage.objects.filter(company_id=company_id)
        transcript = '\n'.join([m.message for m in messages])
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Analyze customer sentiment, root causes of issues, and suggest proactive support actions for this transcript:\n{transcript}"
        result = gemini.generate(prompt)
        return Response({'cx_optimization': result})

# --- Ticket Automation: Categorization, Prioritization, Incident Linking (Demo) ---
class TicketAutomationView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        description = request.data.get('description')
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Categorize, prioritize, and suggest incident links for this ticket description:\n{description}"
        result = gemini.generate(prompt)
        return Response({'automation': result})

# --- Knowledge Base Improvement (Demo) ---
class KnowledgeBaseImprovementView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, company_id):
        faqs = getattr(Company.objects.get(id=company_id), 'faqs', [])
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = f"Analyze these FAQs and suggest improvements or missing topics:\n{faqs}"
        result = gemini.generate(prompt)
        return Response({'kb_improvement': result})

from rest_framework import generics, permissions

class UploadedFileListView(generics.ListAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAdminUser]

class UploadedFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [permissions.IsAdminUser]
