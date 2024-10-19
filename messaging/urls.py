from django.urls import path
from . import views


urlpatterns = [
    path('api/push_notifications', views.send_notifications)
]
