from django.db import models
from django.utils import timezone
from user_management.models import User
from book_catalog.models import Book, Author

class Event(models.Model):
    EVENT_TYPES = [
        ('BOOK_LAUNCH', 'Book Launch'),
        ('READING_CLUB', 'Reading Club'),
        ('WORKSHOP', 'Workshop'),
        ('AUTHOR_VISIT', 'Author Visit'),
        ('CHILDREN_EVENT', 'Children\'s Event'),
        ('EXHIBITION', 'Exhibition'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('UPCOMING', 'Upcoming'),
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField()
    registration_deadline = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='UPCOMING')
    
    # Optional relations
    related_books = models.ManyToManyField(
        Book, blank=True, related_name='events')
    featured_authors = models.ManyToManyField(
        Author, blank=True, related_name='featured_events')
    organizer = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='organized_events')
    
    # Media
    image = models.ImageField(
        upload_to='event_images/', blank=True, null=True)
    attachment = models.FileField(
        upload_to='event_attachments/', blank=True, null=True)
    
    # Additional fields
    is_public = models.BooleanField(default=True)
    requires_registration = models.BooleanField(default=True)
    registration_fee = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def is_full(self):
        return self.registrations.count() >= self.capacity

    @property
    def available_seats(self):
        return max(0, self.capacity - self.registrations.count())

    @property
    def registration_closed(self):
        return timezone.now() > self.registration_deadline

class EventRegistration(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('ATTENDED', 'Attended'),
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='event_registrations')
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    check_in_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class EventFeedback(models.Model):
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=False)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"Feedback for {self.event.title} by {self.user.username}"

class EventResource(models.Model):
    RESOURCE_TYPES = [
        ('DOCUMENT', 'Document'),
        ('PRESENTATION', 'Presentation'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
        ('OTHER', 'Other'),
    ]

    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES)
    file = models.FileField(upload_to='event_resources/')
    is_public = models.BooleanField(default=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.title} - {self.event.title}" 