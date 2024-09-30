# payment/urls.py

from django.urls import path
from .import views

urlpatterns = [
    path('', views.create_checkout_session, name='create-payment-intent'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('details/', views.get_payment_details, name = 'payment_details'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    # path('test-payment-success/', views.test_payment_success, name='test_payment_success'),
]
