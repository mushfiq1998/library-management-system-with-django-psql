from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from user_management.models import User

class DigitalContent(models.Model):
    CONTENT_TYPES = [
        ('EBOOK', 'eBook'),
        ('AUDIOBOOK', 'Audiobook'),
    ]
    
    FILE_FORMATS = [
        ('PDF', 'PDF'),
        ('EPUB', 'EPUB'),
        ('MOBI', 'MOBI'),
        ('MP3', 'MP3'),
        ('M4B', 'M4B'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    file_format = models.CharField(max_length=10, choices=FILE_FORMATS)
    file = models.FileField(
        upload_to='digital_content/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'epub', 'mobi', 'mp3', 'm4b'])]
    )
    cover_image = models.ImageField(upload_to='digital_content/covers/', blank=True, null=True)
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()
    publisher = models.CharField(max_length=200)
    language = models.CharField(max_length=50)
    size_mb = models.DecimalField(max_digits=6, decimal_places=2)
    duration_minutes = models.IntegerField(null=True, blank=True)  # For audiobooks
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()})"

class DigitalLoan(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('RETURNED', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='digital_loans')
    content = models.ForeignKey(DigitalContent, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')
    download_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.content.title}"

    def is_overdue(self):
        return self.status == 'ACTIVE' and timezone.now() > self.due_date

class DigitalContentReview(models.Model):
    content = models.ForeignKey(DigitalContent, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['content', 'user']

    def __str__(self):
        return f"Review by {self.user.username} for {self.content.title}"

class DigitalContentProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.ForeignKey(DigitalContent, on_delete=models.CASCADE)
    current_page = models.IntegerField(default=0)  # For eBooks
    current_position = models.IntegerField(default=0)  # For audiobooks (in seconds)
    last_accessed = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    bookmarks = models.JSONField(default=list)
    notes = models.JSONField(default=dict)

    class Meta:
        unique_together = ['user', 'content']

    def __str__(self):
        return f"Progress for {self.content.title} by {self.user.username}" 