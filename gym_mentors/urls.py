from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_mentor, name="manage_mentor"),
    path('mentor_login/', views.mentor_login, name="mentor_login"),
    path('mentor_refresh/', views.refresh_token, name="mentor_refresh_token")
]