from django import forms
from bookapp.models import Book, Author
from django.core.exceptions import ValidationError

class BookForm(forms.ModelForm):
    # Campo personalizado para escribir nombres de autores separados por comas
    authors_text = forms.CharField(
        required=False,
        label='Authors',
        help_text='Enter author names separated by commas (e.g., John Doe, Jane Smith)',
        widget=forms.TextInput(attrs={'placeholder': 'Author Name, Author Name'})
    )
    
    # Campo para solo el año de publicación
    published_year = forms.IntegerField(
        label='Published Year',
        min_value=1000,
        max_value=2100,
        widget=forms.NumberInput(attrs={'placeholder': 'YYYY'})
    )
    
    read_year = forms.IntegerField(
        required=False,
        label='Read Year',
        min_value=1000,
        max_value=2100,
        widget=forms.NumberInput(attrs={'placeholder': 'YYYY'})
    )
    
    class Meta:
        model = Book
        fields = ['title', 'pages', 'rating', 'status', 'cover_image']
        # Mensajes de error personalizados para los campos del modelo
        error_messages = {
            'title': {
                'required': 'The title is mandatory',
                'max_length': 'The title must be less than 50 characters long',
            },
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Si estamos editando, cargar los autores existentes
            authors = self.instance.authors.all()
            if authors:
                self.initial['authors_text'] = ', '.join([f"{a.name} {a.last_name}" for a in authors])
            
            # Cargar el año de publicación
            if self.instance.published_date:
                self.initial['published_year'] = self.instance.published_date.year
            
            # Cargar el año de lectura
            if self.instance.read_date:
                self.initial['read_year'] = self.instance.read_date.year
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("The title is mandatory")
        if len(title) > 50:
            raise ValidationError("The title must be less than 50 characters long")
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        read_year = cleaned_data.get('read_year')
        published_year = cleaned_data.get('published_year')
        
        if read_year and published_year and read_year < published_year:
            raise ValidationError({
                'read_year': "The read year must be after the published year"
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        from datetime import date
        
        instance = super().save(commit=False)
        
        # Convertir el año a fecha (01 de enero de ese año)
        published_year = self.cleaned_data.get('published_year')
        if published_year:
            instance.published_date = date(published_year, 1, 1)
        
        read_year = self.cleaned_data.get('read_year')
        if read_year:
            instance.read_date = date(read_year, 1, 1)
        else:
            instance.read_date = None
        
        if commit:
            instance.save()
            
            # Procesar los autores
            authors_text = self.cleaned_data.get('authors_text', '')
            instance.authors.clear()
            
            if authors_text:
                author_names = [name.strip() for name in authors_text.split(',')]
                for full_name in author_names:
                    if full_name:
                        # Separar nombre y apellido
                        parts = full_name.split()
                        if len(parts) >= 2:
                            name = parts[0]
                            last_name = ' '.join(parts[1:])
                        else:
                            name = full_name
                            last_name = ''
                        
                        # Crear o obtener el autor
                        author, created = Author.objects.get_or_create(
                            name=name,
                            last_name=last_name
                        )
                        instance.authors.add(author)
            
            self.save_m2m()
        
        return instance
