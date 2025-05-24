from django.db import models
from django.contrib.auth.models import User # Import Django's User model

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    company_email = models.EmailField(blank=True, null=True)
    business_type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user_email = models.EmailField()
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50, default='open')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"

class UploadedFile(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_files', null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
