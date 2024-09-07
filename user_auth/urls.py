from django.urls import path
from . import views

urlpatterns = [
    path('user_register', views.manage_user_register, name="user_register"),
    path('user_login', views.user_login, name="user_login"),
    path('admin_register', views.manage_admin_register, name="admin_register"),
    path('admin_login', views.admin_login, name="admin_login"),
    path('refresh/', views.refresh_token, name="refresh"),
    path('superlogin/', views.superuser_login, name = "superlogin"),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', views.send_password_reset_email, name='password_reset'),
    path('password_reset/confirm/', views.reset_password_confirm, name='password_reset_confirm'),
]