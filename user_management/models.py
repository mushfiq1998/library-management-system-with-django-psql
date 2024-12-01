from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        LIBRARIAN = 'LIBRARIAN', 'Librarian'
        STUDENT = 'STUDENT', 'Student'
        STAFF = 'STAFF', 'Staff'

    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        default=Role.STUDENT
    )
    
    def __str__(self):
        return f"{self.username} - {self.role}"

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    library_card_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    registration_date = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"
