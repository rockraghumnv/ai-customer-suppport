from django.db import models

class Company(models.Model):
    #All are mandatory fields
    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, unique=True)
    company_email = models.EmailField(unique=True)
    business_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
