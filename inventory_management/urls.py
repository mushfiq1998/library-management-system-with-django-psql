from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('<int:pk>/', views.inventory_detail, name='inventory_detail'),
    path('<int:pk>/adjust/', views.adjust_inventory, name='adjust_inventory'),
    path('<int:pk>/report-damaged/', views.report_damaged, name='report_damaged'),
    path('damaged/<int:damaged_id>/update/', 
         views.update_damaged_status, name='update_damaged_status'),
    
    # New CRUD URLs for InventoryItem
    path('items/create/', views.inventory_item_create, name='inventory_item_create'),
    path('items/<int:pk>/edit/', views.inventory_item_edit, name='inventory_item_edit'),
    path('items/<int:pk>/delete/', views.inventory_item_delete, name='inventory_item_delete'),
] 