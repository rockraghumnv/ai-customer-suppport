from rest_framework import serializers
from companies.models import Company
from tickets.models import Ticket
from knowledge_base.models import UploadedFile
from rest_framework.exceptions import ValidationError
from products.models import Product
from services.models import Service
from chat.models import ChatMessage
from analytics.models import Feedback   
from drf_yasg.utils import swagger_serializer_method

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'
        ref_name = "SupportTicketSerializer"

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'
        ref_name = "SupportUploadedFileSerializer"

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'company', 'user_email', 'rating', 'comment', 'created_at']
