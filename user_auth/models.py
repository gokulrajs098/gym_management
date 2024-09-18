from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUserRegistration(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15)
    country = models.CharField(max_length=20)
    gym_name = models.CharField(max_length=20)
    gym_address = models.TextField()
    gym_phone_number = models.CharField(max_length=20)
    is_logged_in = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )