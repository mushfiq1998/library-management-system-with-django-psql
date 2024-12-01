from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/create/', views.book_create, name='book_create'),
    path('books/<int:pk>/edit/', views.book_edit, name='book_edit'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('authors/create/', views.author_create, name='author_create'),
    
    path('genres/', views.genre_list, name='genre_list'),
    path('genres/create/', views.genre_create, name='genre_create'),
    path('authors/<int:pk>/edit/', views.author_edit, name='author_edit'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),
    path('authors/<int:pk>/pdf/', views.author_pdf, name='author_pdf'),
    path('books/<int:pk>/pdf/', views.book_pdf, name='book_pdf'),
    path('books/pdf/', views.book_list_pdf, name='book_list_pdf'),
    path('books/<int:pk>/location/', views.manage_book_location, name='manage_book_location'),
    path('api/shelf/<int:shelf_id>/positions/', views.get_shelf_positions, name='get_shelf_positions'),
    path('shelves/', views.shelf_list, name='shelf_list'),
    path('shelves/create/', views.shelf_create, name='shelf_create'),
    path('shelves/<int:pk>/edit/', views.shelf_edit, name='shelf_edit'),
    path('shelves/<int:pk>/delete/', views.shelf_delete, name='shelf_delete'),
    path('books/<int:pk>/availability/', views.update_book_availability, name='update_book_availability'),
] 