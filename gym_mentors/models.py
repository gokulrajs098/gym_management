from django.db import models
import uuid
from user_auth.models import CustomUserRegistration
from gym_details.models import GymDetails

class Mentors(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username =  models.CharField(max_length=50)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    expertise = models.CharField(max_length=50)
    email=models.EmailField()
    password=models.CharField(max_length=200)
    phone_number=models.CharField(max_length=20)
    admin = models.ForeignKey(CustomUserRegistration, related_name='mentors',null=True, blank=True,on_delete=models.CASCADE )
    Gym = models.ForeignKey(GymDetails, on_delete=models.CASCADE, related_name='mentors', null=True, blank=True)
    is_login = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.admin and not self.admin.is_staff:
            raise ValueError("Only staff users can be assigned to a gym")
        super().save(*args, **kwargs)