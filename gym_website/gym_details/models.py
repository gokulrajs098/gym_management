from django.db import models
from django.conf import settings
from user_auth.models import CustomUserRegistration  # Import your custom user model
import uuid

class GymDetails(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gym_name = models.CharField(max_length=30)
    gym_owner_first_name = models.CharField(max_length=50)
    gym_owner_last_name = models.CharField(max_length=50)
    gym_address = models.CharField(max_length=100)
    gym_phone_number = models.CharField(max_length=20)
    gym_email = models.EmailField()
    admin = models.ForeignKey(CustomUserRegistration, on_delete=models.CASCADE, related_name='gym', null=True, blank=True)
    promo_code_offers = models.BooleanField(default=False)
    promo_code = models.CharField(max_length=30)
    stripe_account_id = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if self.admin and not self.admin.is_staff:
            raise ValueError("Only staff users can be assigned to a gym")
        super().save(*args, **kwargs)