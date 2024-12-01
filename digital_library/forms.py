from django import forms
from .models import DigitalContent, DigitalContentReview

class DigitalContentForm(forms.ModelForm):
    class Meta:
        model = DigitalContent
        fields = [
            'title', 'author', 'description', 'content_type', 'file_format',
            'file', 'cover_image', 'isbn', 'publication_date', 'publisher',
            'language', 'size_mb', 'duration_minutes'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'duration_minutes': forms.NumberInput(attrs={'min': 0}),
            'size_mb': forms.NumberInput(attrs={'min': 0, 'step': '0.01'})
        }

class DigitalContentReviewForm(forms.ModelForm):
    class Meta:
        model = DigitalContentReview
        fields = ['rating', 'review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            }),
            'rating': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class DigitalContentSearchForm(forms.Form):
    SORT_CHOICES = [
        ('title', 'Title'),
        ('author', 'Author'),
        ('publication_date', 'Publication Date'),
        ('rating', 'Rating'),
    ]

    query = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by title, author, or ISBN'
    }))
    content_type = forms.ChoiceField(
        choices=[('', 'All')] + DigitalContent.CONTENT_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    file_format = forms.ChoiceField(
        choices=[('', 'All')] + DigitalContent.FILE_FORMATS,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    ) 