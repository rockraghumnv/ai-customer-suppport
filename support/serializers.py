from rest_framework import serializers
<<<<<<< HEAD
from companies.models import Company
from tickets.models import Ticket
from knowledge_base.models import UploadedFile
from rest_framework.exceptions import ValidationError
=======
from .models import Company, Ticket, UploadedFile, Product, Service, ChatMessage, Feedback
>>>>>>> cd67d2aec22586fc568a9a49933775b19793c4b4

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'

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
