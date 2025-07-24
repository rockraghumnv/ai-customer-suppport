from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from knowledge_base.models import UploadedFile
from products.models import  Product
from services.models import Service
from .serializers import UploadedFileSerializer
from products.serializers import ProductSerializer 
from services.serializers import ServiceSerializer
from .agents.chroma_utils import process_file_for_chroma
from companies.models import Company

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
        file_serializer = self.get_serializer(data=request.data)
        file_serializer.is_valid(raise_exception=True)
        uploaded_file_instance = file_serializer.save(company=company)
        try:
            process_file_for_chroma(uploaded_file_instance)
        except Exception as e:
            print(f"Error processing file for ChromaDB: {e}")
            return Response({'error': f'File uploaded but failed to process for knowledge base: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(file_serializer.data, status=status.HTTP_201_CREATED)

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
