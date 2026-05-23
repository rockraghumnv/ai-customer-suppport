from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from langchain_google_genai import GoogleGenerativeAI
from companies.models import Company
from .models import UploadedFile, FAQ
from .serializers import UploadedFileSerializer, FAQSerializer
from support.agents.chroma_utils import process_file_for_chroma


class FileUploadView(generics.CreateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = UploadedFileSerializer

    def post(self, request, *args, **kwargs):
        company_id = request.data.get('company')
        uploaded_file = request.data.get('file')

        if not company_id or not uploaded_file:
            return Response({'error': 'Company ID and file are required.'}, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = [
            'text/plain', 'application/pdf', 'application/json',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'image/png', 'image/jpeg', 'image/jpg', 'image/bmp', 'image/gif', 'image/webp'
        ]
        if uploaded_file.content_type not in allowed_types:
            return Response(
                {'error': f'Unsupported file type: {uploaded_file.content_type}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded_file.size > 10 * 1024 * 1024:
            return Response({'error': 'File too large (max 10MB).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            return Response({'error': 'Company not found.'}, status=status.HTTP_404_NOT_FOUND)

        file_serializer = self.get_serializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        uploaded_file_instance = file_serializer.save(company=company)

        try:
            process_file_for_chroma(uploaded_file_instance)
        except Exception as exc:
            print(f"Error processing file for ChromaDB: {exc}")
            return Response(
                {'error': f'File uploaded but failed to process for knowledge base: {exc}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(file_serializer.data, status=status.HTTP_201_CREATED)


class UploadedFileListCreateView(generics.ListCreateAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer


class UploadedFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer


class KnowledgeBaseImprovementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, company_id):
        files = UploadedFile.objects.filter(company_id=company_id)
        file_names = [file.file.name for file in files]
        gemini = GoogleGenerativeAI(model="models/gemini-1.5-flash")
        prompt = (
            "Analyze these knowledge base files and suggest improvements or missing topics:\n"
            f"{file_names}"
        )
        result = gemini.generate(prompt)
        return Response({'kb_improvement': result})


class FAQListCreateView(generics.ListCreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer


class FAQDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
