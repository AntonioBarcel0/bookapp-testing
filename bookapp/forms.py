from django import forms
from bookapp.models import Book
from django.core.exceptions import ValidationError

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'pages', 'rating', 'status', 'published_date', 'read_date', 'authors', 'cover_image']
        # Mensajes de error personalizados para los campos del modelo
        error_messages = {
            'title': {
                'required': 'The title is mandatory',
                'max_length': 'The title must be less than 50 characters long',
            },
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("The title is mandatory")
        if len(title) > 50:
            raise ValidationError("The title must be less than 50 characters long")
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        read_date = cleaned_data.get('read_date')
        published_date = cleaned_data.get('published_date')
        
        if read_date and published_date and read_date < published_date:
            raise ValidationError({
                'read_date': "The read date must be after the published date"
            })
        
        return cleaned_data
