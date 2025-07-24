from django.contrib import admin
<<<<<<< HEAD
from companies.models import Company
from tickets.models import Ticket 
from knowledge_base.models import UploadedFile
=======
from .models import Company, Ticket, UploadedFile, Product, Service, ChatMessage, Feedback
>>>>>>> cd67d2aec22586fc568a9a49933775b19793c4b4

# Register your models here.
admin.site.register(Company)
admin.site.register(Ticket)
admin.site.register(UploadedFile)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(ChatMessage)
admin.site.register(Feedback)
