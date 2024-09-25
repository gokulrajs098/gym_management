from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_mentor, name="manage_mentor"),
    path('login/', views.mentor_login, name='mentor-login'),
    path('logout/', views.mentor_logout, name='mentor-logout'),
]