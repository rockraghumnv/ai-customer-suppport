from django.urls import path
from .views import UploadedFileListCreateView, UploadedFileDetailView

urlpatterns = [
    path('', UploadedFileListCreateView.as_view(), name='uploadedfile-list-create'),
    path('<int:pk>/', UploadedFileDetailView.as_view(), name='uploadedfile-detail'),
]
