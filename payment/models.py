from django.db import models
from gym_products.models import GymProducts
from user_auth.models import CustomUserRegistration
from gym_details.models import GymDetails
import uuid
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    PAYMENT_STATUS_CHOICES = [
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    stripe_payment_id = models.CharField(max_length=255)
    plan_name = models.CharField(max_length=50, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUserRegistration, on_delete=models.SET_NULL, null=True)
    gym = models.ForeignKey(GymDetails, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.stripe_payment_id} - {self.status}"
    

class Orders(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    product_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    gym_id = models.CharField(max_length=50)
    address = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=30)
    payment_type = models.CharField(max_length=100)
    country = models.CharField(max_length=50)
    pin_code = models.CharField(max_length=10)
