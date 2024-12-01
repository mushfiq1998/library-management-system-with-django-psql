from django.contrib import admin
from .models import DigitalContent, DigitalLoan, DigitalContentReview, DigitalContentProgress

@admin.register(DigitalContent)
class DigitalContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'content_type', 'file_format', 'is_active')
    list_filter = ('content_type', 'file_format', 'is_active')
    search_fields = ('title', 'author', 'isbn')

@admin.register(DigitalLoan)
class DigitalLoanAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'loan_date', 'due_date', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'content__title')

@admin.register(DigitalContentReview)
class DigitalContentReviewAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('content__title', 'user__username')

@admin.register(DigitalContentProgress)
class DigitalContentProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'completed', 'last_accessed')
    list_filter = ('completed',)
    search_fields = ('user__username', 'content__title') 