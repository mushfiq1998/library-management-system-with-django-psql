from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    # Membership URLs
    path('memberships/', views.membership_list, name='membership_list'),
    path('memberships/create/', views.membership_create, name='membership_create'),
    path('memberships/<int:pk>/edit/', views.membership_edit, name='membership_edit'),
    path('memberships/<int:membership_id>/activities/', views.member_activities, name='member_activities'),
    
    # Membership Plan URLs
    path('plans/', views.membership_plan_list, name='membership_plan_list'),
    path('plans/create/', views.membership_plan_create, name='membership_plan_create'),
    path('plans/<int:pk>/edit/', views.membership_plan_edit, name='membership_plan_edit'),
    path('plans/<int:pk>/delete/', views.membership_plan_delete, name='membership_plan_delete'),
    
    # Member Activity URLs
    path('activities/', views.activity_list, name='activity_list'),
    path('activities/create/', views.activity_create, name='activity_create'),
    path('activities/<int:pk>/edit/', views.activity_edit, name='activity_edit'),
    path('activities/<int:pk>/delete/', views.activity_delete, name='activity_delete'),
    
    # Renewal Reminder URLs
    path('reminders/', views.renewal_reminders, name='renewal_reminders'),
    path('reminders/create/', views.reminder_create, name='reminder_create'),
    path('reminders/<int:pk>/edit/', views.reminder_edit, name='reminder_edit'),
    path('reminders/<int:pk>/delete/', views.reminder_delete, name='reminder_delete'),
    path('reminders/<int:reminder_id>/response/', views.update_reminder_response, name='update_reminder_response'),
] 