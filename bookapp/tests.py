from django.test import TestCase, Client
from django.contrib.auth.models import User, Group, Permission
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from datetime import date
from bookapp.models import Book, Author
from bookapp.forms import BookForm


class BookModelTest(TestCase):
    """Tests para el modelo Book"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.author = Author.objects.create(
            name="Gabriel",
            last_name="García Márquez"
        )

    def test_book_creation_correct_without_author_and_cover(self):
        """Test: Creación correcta sin autores y sin portada"""
        book = Book.objects.create(
            title="Cien años de soledad",
            pages=100,
            status="PE",
            published_date=date(2020, 1, 1)
        )
        self.assertEqual(book.title, "Cien años de soledad")
        self.assertEqual(book.pages, 100)
        self.assertEqual(book.status, "PE")
        self.assertIsNone(book.rating)
        self.assertIsNone(book.read_date)

    def test_book_with_incorrect_pages(self):
        """Test: Con un número de páginas incorrecto (menor que 1)"""
        book = Book(
            title="Test Book",
            pages=0,  # BUG ENCONTRADO: El modelo acepta 0, pero debe ser mínimo 1
            status="PE",
            published_date=date(2020, 1, 1)
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_book_with_incorrect_rating(self):
        """Test: Con un rating incorrecto (fuera del rango 1-5)"""
        # Rating menor que 1
        book = Book(
            title="Test Book",
            pages=100,
            rating=0,
            status="PE",
            published_date=date(2020, 1, 1)
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

        # Rating mayor que 5
        book2 = Book(
            title="Test Book 2",
            pages=100,
            rating=6,
            status="PE",
            published_date=date(2020, 1, 1)
        )
        with self.assertRaises(ValidationError):
            book2.full_clean()

    def test_book_with_read_date_before_published_date(self):
        """Test: Con una fecha de lectura anterior a la fecha de publicación"""
        # BUG ENCONTRADO: La validación en models.py está al revés
        book = Book(
            title="Test Book",
            pages=100,
            status="FI",
            published_date=date(2020, 1, 1),
            read_date=date(2019, 12, 31)
        )
        with self.assertRaises(ValidationError):
            book.full_clean()

    def test_book_with_author(self):
        """Test: Con un autor"""
        book = Book.objects.create(
            title="Test Book",
            pages=100,
            status="PE",
            published_date=date(2020, 1, 1)
        )
        book.authors.add(self.author)
        self.assertEqual(book.authors.count(), 1)
        self.assertEqual(book.authors.first().name, "Gabriel")

    def test_book_with_cover(self):
        """Test: Con una portada"""
        cover = SimpleUploadedFile(
            "cover.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        book = Book.objects.create(
            title="Test Book",
            pages=100,
            status="PE",
            published_date=date(2020, 1, 1),
            cover_image=cover
        )
        self.assertTrue(book.cover_image)
        self.assertIn("covers/", book.cover_image.name)


class BookFormTest(TestCase):
    """Tests para el formulario BookForm"""

    def setUp(self):
        """Configuración inicial para los tests"""
        self.author = Author.objects.create(
            name="Isabel",
            last_name="Allende"
        )

    def test_form_creation_correct_without_author_and_cover(self):
        """Test: Creación correcta sin autores y sin portada"""
        form_data = {
            'title': 'La casa de los espíritus',
            'pages': 200,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_title_over_50_characters(self):
        """Test: Con título de más de 50 caracteres y comprobar mensaje de error"""
        form_data = {
            'title': 'A' * 51,  # 51 caracteres
            'pages': 200,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(
            form.errors['title'][0],
            "The title must be less than 50 characters long"
        )

    def test_form_with_empty_title(self):
        """Test: Con título vacío y comprobar mensaje de error"""
        form_data = {
            'title': '',
            'pages': 200,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertEqual(
            form.errors['title'][0],
            "The title is mandatory"
        )

    def test_form_with_incorrect_pages(self):
        """Test: Con un número de páginas incorrecto"""
        form_data = {
            'title': 'Test Book',
            'pages': 0,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('pages', form.errors)

    def test_form_with_incorrect_rating(self):
        """Test: Con un rating incorrecto"""
        # Rating menor que 1
        form_data = {
            'title': 'Test Book',
            'pages': 100,
            'rating': 0,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Rating mayor que 5
        form_data['rating'] = 6
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_with_read_date_before_published_date(self):
        """Test: Con una fecha de lectura anterior a la fecha de publicación y comprobar mensaje de error"""
        form_data = {
            'title': 'Test Book',
            'pages': 100,
            'status': 'FI',
            'published_date': '2020-01-01',
            'read_date': '2019-12-31'
        }
        form = BookForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('read_date', form.errors)
        self.assertEqual(
            form.errors['read_date'][0],
            "The read date must be after the published date"
        )

    def test_form_with_author(self):
        """Test: Con un autor"""
        form_data = {
            'title': 'Test Book',
            'pages': 100,
            'status': 'RE',
            'published_date': '2020-01-01',
            'authors': [self.author.id]
        }
        form = BookForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_with_cover(self):
        """Test: Con una portada"""
        cover = SimpleUploadedFile(
            "test_cover.jpg",
            b"file_content",
            content_type="image/jpeg"
        )
        form_data = {
            'title': 'Test Book',
            'pages': 100,
            'status': 'RE',
            'published_date': '2020-01-01'
        }
        form = BookForm(data=form_data, files={'cover_image': cover})
        self.assertTrue(form.is_valid())


class BookViewsTest(TestCase):
    """Tests para los controladores/vistas"""

    def setUp(self):
        """Configuración inicial: crear usuarios y permisos"""
        # Crear grupo Admin con todos los permisos
        self.admin_group = Group.objects.create(name='Admin')
        permissions = Permission.objects.filter(
            content_type__app_label='bookapp',
            content_type__model='book'
        )
        for perm in permissions:
            self.admin_group.permissions.add(perm)

        # Usuario admin
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123'
        )
        self.admin_user.groups.add(self.admin_group)

        # Usuario autenticado sin permisos
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regular123'
        )

        # Crear un libro de prueba
        self.book = Book.objects.create(
            title='Test Book',
            pages=100,
            status='PE',
            published_date=date(2020, 1, 1)
        )

        self.client = Client()

    def test_form_route_with_admin_user(self):
        """Test: Ruta form con usuario Admin"""
        # BUG ENCONTRADO: BookCreate debe tener PermissionRequiredMixin, no solo LoginRequiredMixin
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/bookapp/form')
        self.assertEqual(response.status_code, 200)

    def test_form_route_with_regular_user(self):
        """Test: Ruta form con usuario autenticado sin permisos"""
        self.client.login(username='regular', password='regular123')
        response = self.client.get('/bookapp/form')
        # Debe ser 403 Forbidden porque no tiene permiso para crear
        self.assertEqual(response.status_code, 403)

    def test_list_route_with_admin_user(self):
        """Test: Ruta list con usuario Admin"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/bookapp/list')
        self.assertEqual(response.status_code, 200)
        self.assertIn('books', response.context)

    def test_list_route_with_regular_user(self):
        """Test: Ruta list con usuario autenticado sin permisos"""
        self.client.login(username='regular', password='regular123')
        response = self.client.get('/bookapp/list')
        # La lista debe ser accesible para todos
        self.assertEqual(response.status_code, 200)

    def test_edit_route_with_admin_user(self):
        """Test: Ruta <id>/edit con usuario Admin"""
        # BUG ENCONTRADO: La URL debe incluir el pk
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/bookapp/{self.book.pk}/edit')
        self.assertEqual(response.status_code, 200)

    def test_edit_route_with_regular_user(self):
        """Test: Ruta <id>/edit con usuario autenticado sin permisos"""
        self.client.login(username='regular', password='regular123')
        response = self.client.get(f'/bookapp/{self.book.pk}/edit')
        # Debe ser 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_delete_route_with_admin_user(self):
        """Test: Ruta <id>/delete con usuario Admin"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/bookapp/{self.book.pk}/delete')
        self.assertEqual(response.status_code, 200)

    def test_delete_route_with_regular_user(self):
        """Test: Ruta <id>/delete con usuario autenticado sin permisos"""
        self.client.login(username='regular', password='regular123')
        response = self.client.get(f'/bookapp/{self.book.pk}/delete')
        # Debe ser 403 Forbidden
        self.assertEqual(response.status_code, 403)

    def test_detail_route_with_admin_user(self):
        """Test: Ruta <id>/detail con usuario Admin"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get(f'/bookapp/{self.book.pk}/detail')
        self.assertEqual(response.status_code, 200)
        self.assertIn('book', response.context)

    def test_detail_route_with_regular_user(self):
        """Test: Ruta <id>/detail con usuario autenticado sin permisos"""
        self.client.login(username='regular', password='regular123')
        response = self.client.get(f'/bookapp/{self.book.pk}/detail')
        # Debe ser accesible para usuarios autenticados
        self.assertEqual(response.status_code, 200)
