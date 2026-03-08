from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, default='')
    is_manager = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='+',
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='+',
        blank=True,
    )