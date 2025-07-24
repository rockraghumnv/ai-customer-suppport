from django.contrib import admin
from companies.models import Company
from tickets.models import Ticket 
from knowledge_base.models import UploadedFile

# Register your models here.
admin.site.register(Company)
admin.site.register(Ticket)
admin.site.register(UploadedFile)
