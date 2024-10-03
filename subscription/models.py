from django.db import models
import uuid
from gym_details.models import GymDetails
from user_auth.models import CustomUserRegistration

class SubscriptionPlan(models.Model):
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    plan_name = models.CharField(max_length=30)
    desc = models.CharField(max_length=50)
    price = models.IntegerField()
    gym = models.ForeignKey(GymDetails,on_delete=models.CASCADE ,null=True ,blank=True)
    admin = models.ForeignKey(CustomUserRegistration, on_delete=models.CASCADE, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=50, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=50, null=True, blank=True)
    interval = models.CharField(max_length=50)
    interval_count = models.CharField(max_length=50)

    def __str__(self):
        return self.plan_name