from django.db import models
import uuid
from user_auth.models import CustomUserRegistration
from gym_details.models import GymDetails

class Customer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending')
    ]
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(CustomUserRegistration,related_name='customers',on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    plan_status = models.CharField(choices=STATUS_CHOICES, max_length=10)
    plan_name = models.CharField(max_length=30)
    plan_start_date = models.DateTimeField()
    plan_end_date = models.DateTimeField()
    gym = models.ForeignKey(GymDetails, related_name='customers', on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=100, null=True)
