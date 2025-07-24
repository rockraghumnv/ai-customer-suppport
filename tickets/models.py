from django.db import models
from companies.models import Company
from django.contrib.auth.models import User

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
        return f"Ticket #{{self.id}} - {{self.subject}}"
