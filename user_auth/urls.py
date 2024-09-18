from django.urls import path
from . import views

urlpatterns = [
    path('user_register', views.manage_user_register, name="user_register"),
    path('user_login', views.user_login, name="user_login"),
    path('admin_register', views.manage_admin_register, name="admin_register"),
    path('admin_login', views.admin_login, name="admin_login"),
    path('superlogin/', views.superuser_login, name = "superlogin"),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.send_password_reset_email, name='password-reset'),
    path('password-reset-confirm/<uidb64>/<token>/', views.reset_password, name='password-reset-confirm'),
]