from django.urls import path
from . import views


urlpatterns = [
    path('api/push-notifications', views.send_notifications),
    path('api/token-add-user', views.add_token_user),
    path('api/token-add-customer', views.add_token_customer),
]
