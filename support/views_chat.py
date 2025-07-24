from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from chat.models import ChatMessage
from chat.serializers import ChatMessageSerializer
from .agents.agent_router import route_query_to_agent
from knowledge_base.models import UploadedFile, Company, Ticket
from .agents.copilot_agent import CopilotAgent
from PIL import Image
import pytesseract

class ChatMessageListView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return ChatMessage.objects.filter(ticket_id=ticket_id).order_by('created_at')
        return ChatMessage.objects.none()

class ChatbotInteractionView(APIView):
    parser_classes = (MultiPartParser, FormParser)
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
                image = Image.open(image_file)
                extracted_text = pytesseract.image_to_string(image)
            except Exception as e:
                extracted_text = f"[Image uploaded, but text extraction failed: {e}]"
        user_msg = ChatMessage.objects.create(
            company=company,
            user_email=user_email,
            sender='user',
            message=query,
            image=chat_image
        )
        full_query = query
        if extracted_text:
            full_query = f"{query}\n\nImage context: {extracted_text}"
        try:
            agent_response = route_query_to_agent(full_query, company, user_email)
            if isinstance(agent_response, Ticket):
                if uploaded_file_instance:
                    uploaded_file_instance.ticket = agent_response
                    uploaded_file_instance.save()
                ChatMessage.objects.create(
                    ticket=agent_response,
                    company=company,
                    user_email=user_email,
                    sender='agent',
                    message='A support ticket has been created for you. Our team will assist you shortly.'
                )
                from .serializers import TicketSerializer
                ticket_serializer = TicketSerializer(agent_response)
                return Response({'message': 'I couldn\'t find an immediate answer. A support ticket has been created for you.', 'ticket': ticket_serializer.data}, status=status.HTTP_201_CREATED)
            else:
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

class CopilotSummaryView(APIView):
    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)
        agent = CopilotAgent(ticket)
        summary = agent.summarize_and_suggest()
        return Response({'summary': summary}, status=status.HTTP_200_OK)
