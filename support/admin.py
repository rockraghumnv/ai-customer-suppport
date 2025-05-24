from django.contrib import admin
from .models import Company, Ticket, UploadedFile

# Register your models here.
admin.site.register(Company)
admin.site.register(Ticket)
admin.site.register(UploadedFile)
