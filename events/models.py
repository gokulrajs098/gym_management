from django.db import models
import uuid
from gym_details.models import GymDetails
from gym_mentors.models import Mentors

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    date = models.DateField()
    timing = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    description = models.TextField()
    guest_name = models.CharField(max_length=255, blank=True, null=True)
    gym = models.ForeignKey(GymDetails, on_delete=models.CASCADE, related_name='events')

    def _str_(self):
        return f"{self.name} at {self.gym.gym_name}"