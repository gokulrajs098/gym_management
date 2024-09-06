from django.db import models
from django.conf import settings
from gym_details.models import GymDetails
from user_auth.models import CustomUserRegistration

class GymAttendance(models.Model):
    user = models.ForeignKey(CustomUserRegistration, on_delete=models.CASCADE)
    gym = models.ForeignKey(GymDetails, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.gym} - {'Checked In' if self.checked_in else 'Checked Out'}"