from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from companies.models import Company
from tickets.models import Ticket
from tickets.serializers import TicketSerializer
from knowledge_base.models import UploadedFile
from chat.models import ChatMessage
from .agents.agent_router import route_query_to_agent
from .agents.copilot_agent import CopilotAgent
from PIL import Image
import pytesseract


class ChatbotInteractionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        query = request.data.get('query')
        company_identifier = request.data.get('company')
        user_email = request.data.get('user_email')
        image_file = request.FILES.get('image')

        if not query or not company_identifier or not user_email:
            return Response(
                {'error': 'Query, company identifier, and user email are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            except Exception as exc:
                extracted_text = f"[Image uploaded, but text extraction failed: {exc}]"

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
                    sender='user',
                    message=query,
                    image=chat_image,
                )
                ChatMessage.objects.create(
                    ticket=agent_response,
                    sender='agent',
                    message='A support ticket has been created for you. Our team will assist you shortly.',
                )
                ticket_serializer = TicketSerializer(agent_response)
                return Response(
                    {
                        'message': 'I couldn\'t find an immediate answer. A support ticket has been created for you.',
                        'ticket': ticket_serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response({'response': agent_response}, status=status.HTTP_200_OK)
        except Exception as exc:
            print(f"Error routing query to agent: {exc}")
            return Response(
                {'error': 'An error occurred while processing your request.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CopilotSummaryView(APIView):
    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({'error': 'Ticket not found.'}, status=status.HTTP_404_NOT_FOUND)

        agent = CopilotAgent(ticket)
        summary = agent.summarize_and_suggest()
        return Response({'summary': summary}, status=status.HTTP_200_OK)
