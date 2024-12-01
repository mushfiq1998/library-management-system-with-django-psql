from django import forms
from .models import Book, Author, Genre, BookLocation, Shelf, Review

class BookForm(forms.ModelForm):
    shelf = forms.ModelChoiceField(
        queryset=Shelf.objects.all(),
        required=False,
        help_text="Select the shelf where this book will be placed"
    )
    row = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'min': 1}),
        help_text="Row number in the shelf"
    )
    column = forms.IntegerField(
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'min': 1}),
        help_text="Column number in the shelf"
    )

    class Meta:
        model = Book
        fields = ['title', 'authors', 'isbn', 'genres', 'publication_date', 
                 'edition', 'summary', 'language']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'summary': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        shelf = cleaned_data.get('shelf')
        row = cleaned_data.get('row')
        column = cleaned_data.get('column')

        # If any location field is provided, all must be provided
        if any([shelf, row, column]) and not all([shelf, row, column]):
            raise forms.ValidationError(
                "If specifying a location, all location fields (shelf, row, and column) must be provided."
            )

        return cleaned_data

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography', 'birth_date', 'death_date']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 4}),
        }

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } 

class BookLocationForm(forms.ModelForm):
    class Meta:
        model = BookLocation
        fields = ['shelf', 'row', 'column']
        widgets = {
            'row': forms.NumberInput(attrs={'min': 1}),
            'column': forms.NumberInput(attrs={'min': 1}),
        }

class ShelfForm(forms.ModelForm):
    class Meta:
        model = Shelf
        fields = ['name', 'description', 'floor', 'section', 'total_rows', 'total_columns']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter shelf name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter shelf description'
            }),
            'floor': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'section': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter section identifier'
            }),
            'total_rows': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'total_columns': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            })
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': '1',
                'max': '5',
                'class': 'form-control'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control'
            })
        }