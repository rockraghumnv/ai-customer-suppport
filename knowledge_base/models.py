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
