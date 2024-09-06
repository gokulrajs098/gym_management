from django.db import models
from user_auth.models import CustomUserRegistration
import uuid
from gym_details.models import GymDetails

class GymProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)
    type = models.CharField(max_length=50)
    desc = models.CharField(max_length=100)
    image = models.ImageField(upload_to='pics')
    reviews = models.CharField(max_length=100)
    stock = models.IntegerField()
    Gym = models.ForeignKey(GymDetails, on_delete=models.CASCADE)
    admin = models.ForeignKey(CustomUserRegistration, on_delete=models.CASCADE, related_name='products')
    stripe_product_id = models.CharField(max_length=50, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.admin and not self.admin.is_staff:
            raise ValueError("Only staff users can add products")
        super().save(*args, **kwargs)  # Call the parent class's save method
