from rest_framework import serializers
from .models import Company, Ticket, UploadedFile
from rest_framework.exceptions import ValidationError

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class TicketSerializer(serializers.ModelSerializer):
    files = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = '__all__'

    def get_files(self, obj):
        # You might want a separate serializer for files if you need more details
        return [file.file.url for file in obj.files.all()]

    def validate(self, data):
        # Check if the instance is being created (not updated)
        if self.instance is None:
            # For creation, check if files are provided or associated
            # This assumes files are uploaded and linked before ticket creation
            # or handled in a specific view logic.
            # A more robust approach might involve checking related files after ticket save
            # or handling file uploads within the ticket creation process.
            # For this validation, we'll assume files are linked post-creation or via a specific flow.
            # A direct check here is difficult without knowing the file upload flow.
            pass # Placeholder - validation depends on file upload implementation

        # If you have a way to link files during ticket creation/update,
        # you would add validation logic here.
        # Example (assuming file IDs are passed in data, which is not standard for FK):
        # if 'files' not in data or not data['files']:
        #     raise ValidationError("At least one file is required for a ticket.")

        return data

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = '__all__'
