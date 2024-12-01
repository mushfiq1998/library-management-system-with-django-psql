from django.urls import path
from . import views

app_name = 'digital_library'

urlpatterns = [
    # Content browsing and search
    path('', views.digital_content_list, name='content_list'),
    path('content/<int:pk>/', views.digital_content_detail, 
         name='content_detail'),
    
    # Content management (staff only)
    path('content/create/', views.digital_content_create,
         name='content_create'),
    path('content/<int:pk>/edit/', views.digital_content_edit,
         name='content_edit'),
    path('content/<int:pk>/delete/', views.digital_content_delete,
         name='content_delete'),
    
    # User interactions
    path('content/<int:pk>/borrow/', views.borrow_digital_content,
         name='borrow_content'),
    path('content/<int:pk>/return/', views.return_digital_content,
         name='return_content'),
    path('content/<int:pk>/review/', views.review_digital_content,
         name='review_content'),
    path('my-loans/', views.my_digital_loans, name='my_loans'),
    
    # Reading/Listening interface
    path('content/<int:pk>/read/', views.read_digital_content,
         name='read_content'),
    path('content/<int:pk>/listen/', views.listen_digital_content,
         name='listen_content'),
    path('content/<int:pk>/download/', views.download_digital_content,
         name='download_content'),
    
    # Progress tracking
    path('content/<int:pk>/progress/update/', views.update_progress,
         name='update_progress'),
    path('content/<int:pk>/bookmark/add/', views.add_bookmark,
         name='add_bookmark'),
    path('content/<int:pk>/note/add/', views.add_note, name='add_note'),
] 