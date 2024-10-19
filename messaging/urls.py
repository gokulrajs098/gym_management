from django.urls import path
from . import views


urlpatterns = [
    path('api/push-notifications', views.send_notifications)
]
