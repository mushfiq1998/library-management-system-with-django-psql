from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_login, name='home'), 
    path('', include('user_management.urls')),
    path('', include('book_catalog.urls')),
    path('circulation/', include(
        'circulation_management.urls', namespace='circulation')),
    path('inventory/', include(
        'inventory_management.urls', namespace='inventory')),
    path('staff/', include(
        'staff_management.urls', namespace='staff')),
    path('membership/', include(
        'membership_management.urls', namespace='membership')),
    path('digital/', include(
        'digital_library.urls', namespace='digital')),
    path('digital-library/', include(
        'digital_library.urls', namespace='digital_library')),
    path('event/', include(
        'event_management.urls', namespace='event')),
    path('finance/', include(
        'finance_management.urls', namespace='finance')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
