from django.db import models
from tickets.models import Ticket
from companies.models import Company

class UploadedFile(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_files', null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


class FAQ(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.name}: {self.question[:50]}"
