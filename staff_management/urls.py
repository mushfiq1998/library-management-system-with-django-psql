from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    # Department URLs
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    # Staff Member URLs
    path('members/', views.staff_member_list, name='staff_member_list'),
    path('members/create/', views.staff_member_create, name='staff_member_create'),
    path('members/<int:pk>/', views.staff_member_detail, name='staff_member_detail'),
    path('members/<int:pk>/edit/', views.staff_member_edit, name='staff_member_edit'),
    path('members/<int:pk>/delete/', views.staff_member_delete, name='staff_member_delete'),
    
    # Leave Management URLs
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/create/', views.leave_create, name='leave_create'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('leaves/<int:pk>/edit/', views.leave_edit, name='leave_edit'),
    path('leaves/<int:pk>/delete/', views.leave_delete, name='leave_delete'),
    path('leaves/<int:pk>/action/', views.leave_action, name='leave_action'),
    
    # Attendance URLs
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/<int:pk>/edit/', views.attendance_edit, name='attendance_edit'),
    path('attendance/<int:pk>/delete/', views.attendance_delete, name='attendance_delete'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    
    # Dashboard
    path('dashboard/', views.staff_dashboard, name='staff_dashboard'),
] 