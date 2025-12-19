from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', views.user_login, name='login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('admin/create/', views.create_admin_user, name='create_admin_user'),
    path('password/change/', views.change_password, name='change_password'),
    # path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'), # Deprecated in favor of root /dashboard/
    path('admin-dashboard/users/', views.manage_users, name='manage_users'),
    path('admin-dashboard/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('admin-dashboard/users/<int:user_id>/toggle/', views.toggle_user_status, name='toggle_user_status'),
]
