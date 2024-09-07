from django.urls import path
from . import views
from .views import StripeCallbackView

urlpatterns = [
    path('', views.manage_gym_details, name="gym_details"),
    path('callback/', StripeCallbackView.as_view(), name='stripe_callback'),
]