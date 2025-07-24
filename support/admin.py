from django.contrib import admin
from companies.models import Company
from tickets.models import Ticket 
from knowledge_base.models import UploadedFile
from products.models import Product
from services.models import Service
from chat.models import ChatMessage
from analytics.models import Feedback

# Register your models here.
admin.site.register(Company)
admin.site.register(Ticket)
admin.site.register(UploadedFile)
admin.site.register(Product)
admin.site.register(Service)
admin.site.register(ChatMessage)
admin.site.register(Feedback)
