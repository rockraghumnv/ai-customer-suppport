from rest_framework import serializers
from .models import UploadedFile, FAQ

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'
        ref_name = "KnowledgeBaseUploadedFileSerializer"


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
