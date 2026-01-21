from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.forms import ValidationError

# Create your models here.

class Author(models.Model):
    # BUG CORREGIDO: Añadido max_length requerido para CharField
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

class Book(models.Model):
    STATUS_CHOICES = [
        ('PE', 'Pending'),
        ('RE', 'Reading'),
        ('FI', 'Finished')
    ]

    title = models.CharField(max_length=50)
    # BUG CORREGIDO: MinValueValidator cambiado de 0 a 1
    pages = models.IntegerField(validators=[MinValueValidator(1)])
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES
    )
    published_date = models.DateField()
    read_date = models.DateField(blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True)
    cover_image = models.FileField(upload_to='covers/', blank=True)

    def clean(self):
        super().clean()
        # BUG CORREGIDO: Cambiado > por < para validar correctamente
        if self.read_date and self.read_date < self.published_date:
            raise ValidationError({"read_date": "The read date must be after the published date"})

    def __str__(self):
        return self.title