from django.contrib.auth.models import AbstractUser
from django.db import models
from companies.models import Company


class User(AbstractUser):
    email = models.EmailField(unique=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="users",
    )

    def __str__(self):
        return self.username
