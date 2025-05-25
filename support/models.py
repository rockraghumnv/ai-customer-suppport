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

class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    manual = models.FileField(upload_to='product_manuals/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'name')

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class Service(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='service_images/', null=True, blank=True)
    document = models.FileField(upload_to='service_docs/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class UploadedFile(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='knowledge_files', null=True, blank=True)
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Add a field to track if this file is active (for replacement/deletion)
    is_active = models.BooleanField(default=True)
    # Optionally, store a file type/category for easier management
    file_type = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.file.name

class ChatMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True, related_name='chat_messages')
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user_email = models.EmailField()
    sender = models.CharField(max_length=20, choices=[('user', 'User'), ('agent', 'Agent')])
    message = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} ({self.user_email}) at {self.created_at}"

class Feedback(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    user_email = models.EmailField()
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback({self.company}, {self.user_email}, {self.rating})"
