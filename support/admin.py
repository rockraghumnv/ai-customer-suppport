from django.contrib import admin
from .models import Company, Ticket, UploadedFile, Product, Service, ChatMessage, Feedback

# Register your models here.
admin.site.register(Company)
admin.site.register(Ticket)
admin.site.register(UploadedFile)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(ChatMessage)
admin.site.register(Feedback)
