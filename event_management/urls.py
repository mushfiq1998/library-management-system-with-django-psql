from django.urls import path
from . import views

app_name = 'event'

urlpatterns = [
    # Event List and Detail Views
    path('', views.event_list, name='event_list'),
    path('<int:pk>/', views.event_detail, name='event_detail'),
    
    # Event Management (Staff Only)
    path('create/', views.event_create, name='event_create'),
    path('<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('<int:pk>/delete/', views.event_delete, name='event_delete'),
    
    # Registration Management
    path('<int:pk>/register/', views.event_register, name='event_register'),
    path('registration/<int:pk>/cancel/', views.registration_cancel, 
         name='registration_cancel'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    
    # Event Resources
    path('<int:pk>/resources/', views.event_resources, name='event_resources'),
    path('<int:pk>/resources/add/', views.resource_add, name='resource_add'),
    path('resources/<int:pk>/delete/', views.resource_delete, name='resource_delete'),
    
    # Feedback
    path('<int:pk>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('<int:pk>/feedback/list/', views.event_feedback_list, 
         name='event_feedback_list'),
    
    # Calendar View
    path('calendar/', views.event_calendar, name='event_calendar'),
    
    # Add this to your urlpatterns
    path('register/', views.create_registration, name='event_register'),
] 