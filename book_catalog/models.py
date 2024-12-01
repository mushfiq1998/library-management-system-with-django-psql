from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import barcode
from barcode.writer import ImageWriter
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model

'''
    A genre is a category or classification that describes the type or style of a book.
'''
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    biography = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('AR', 'Arabic'),
        ('BA', 'Bengali'),
        ('UR', 'Urdu'),
        ('HI', 'Hindi'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(
        Author, related_name='books')
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    genres = models.ManyToManyField(
        Genre, related_name='books')
    publication_date = models.DateField(null=True, blank=True)
    edition = models.CharField(max_length=100, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default='EN')
    barcode = models.ImageField(upload_to='barcodes/', blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    AVAILABILITY_STATUS = [
        ('AVAILABLE', 'Available'),
        ('ISSUED', 'Issued'),
        ('RESERVED', 'Reserved'),
        ('MAINTENANCE', 'Under Maintenance'),
    ]
    
    availability_status = models.CharField(
        max_length=20,
        choices=AVAILABILITY_STATUS,
        default='AVAILABLE'
    )
    availability_notes = models.TextField(
        blank=True,
        help_text="Any notes about the book's availability"
    )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate barcode
        if not self.barcode:
            try:
                # Create custom writer options without text
                writer_options = {
                    'module_width': 0.2,
                    'module_height': 15.0,
                    'quiet_zone': 6.0,
                    'font_size': 10,
                    'text_distance': 5.0,
                    'background': 'white',
                    'foreground': 'black',
                    'write_text': False  # Disable text rendering
                }
                
                EAN = barcode.get_barcode_class('ean13')
                ean = EAN(self.isbn, writer=ImageWriter())
                
                # Apply custom options
                for key, val in writer_options.items():
                    setattr(ean.writer, key, val)
                
                buffer = BytesIO()
                ean.write(buffer)
                self.barcode.save(
                    f'barcode_{self.isbn}.png',
                    File(buffer),
                    save=False
                )
            except Exception as e:
                print(f"Error generating barcode: {str(e)}")

        # Generate QR code
        if not self.qr_code:
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(f'Book: {self.title}\nISBN: {self.isbn}')
                qr.make(fit=True)

                qr_image = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                qr_image.save(buffer, format='PNG')
                self.qr_code.save(
                    f'qr_{self.isbn}.png',
                    File(buffer),
                    save=False
                )
            except Exception as e:
                print(f"Error generating QR code: {str(e)}")

        super().save(*args, **kwargs)

    @property
    def location_display(self):
        try:
            loc = self.location
            return f"Floor {loc.shelf.floor}, Section {loc.shelf.section}, " \
                   f"Shelf {loc.shelf.name}, Row {loc.row}, Column {loc.column}"
        except BookLocation.DoesNotExist:
            return "Location not assigned"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return sum(review.rating for review in reviews) / len(reviews)

class Shelf(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    floor = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Floor number where the shelf is located"
    )
    section = models.CharField(
        max_length=50,
        help_text="Section identifier (e.g., 'A', 'B', 'Science', 'History')"
    )
    total_rows = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of rows in this shelf"
    )
    total_columns = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Number of columns in this shelf"
    )

    def __str__(self):
        return f"{self.name} - Floor {self.floor}, Section {self.section}"

    class Meta:
        unique_together = ['floor', 'section', 'name']

class BookLocation(models.Model):
    book = models.OneToOneField(
        'Book',
        on_delete=models.CASCADE,
        related_name='location'
    )
    shelf = models.ForeignKey(
        Shelf,
        on_delete=models.CASCADE,
        related_name='book_locations'
    )
    row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Row number in the shelf"
    )
    column = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Column number in the shelf"
    )
    added_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.shelf:
            if self.row > self.shelf.total_rows:
                raise ValidationError({
                    'row': f'Row number cannot be greater than shelf\'s total rows ({self.shelf.total_rows})'
                })
            if self.column > self.shelf.total_columns:
                raise ValidationError({
                    'column': f'Column number cannot be greater than shelf\'s total columns ({self.shelf.total_columns})'
                })
            
            # Check if location is already occupied
            existing_location = BookLocation.objects.filter(
                shelf=self.shelf,
                row=self.row,
                column=self.column
            ).exclude(book=self.book).first()
            
            if existing_location:
                raise ValidationError(
                    f'This location is already occupied by book: {existing_location.book.title}'
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.book.title} - Shelf: {self.shelf.name}, Row: {self.row}, Column: {self.column}"

    class Meta:
        unique_together = ['shelf', 'row', 'column']

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['book', 'user']  # One review per book per user

    def __str__(self):
        return f"Review by {self.user.username} for {self.book.title}"
