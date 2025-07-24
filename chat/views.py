from rest_framework import generics
from .models import ChatMessage
from .serializers import ChatMessageSerializer

class ChatMessageListCreateView(generics.ListCreateAPIView):
    queryset = ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        ticket_id = self.request.query_params.get('ticket')
        if ticket_id:
            return self.queryset.filter(ticket_id=ticket_id)
        return self.queryset
