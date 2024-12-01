from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='user_management/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Protected URLs (require login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('manage-users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
] 