from django.urls import path
from .views import (
    FileUploadView,
    UploadedFileListCreateView,
    UploadedFileDetailView,
    KnowledgeBaseImprovementView,
    FAQListCreateView,
    FAQDetailView,
)

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('', UploadedFileListCreateView.as_view(), name='uploadedfile-list-create'),
    path('<int:pk>/', UploadedFileDetailView.as_view(), name='uploadedfile-detail'),
    path('kb-improvement/<int:company_id>/', KnowledgeBaseImprovementView.as_view(), name='kb-improvement'),
    path('faqs/', FAQListCreateView.as_view(), name='faq-list-create'),
    path('faqs/<int:pk>/', FAQDetailView.as_view(), name='faq-detail'),
]
