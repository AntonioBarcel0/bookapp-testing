# Testing en Django - Gestión de Libros

Proyecto de la práctica de testing para la asignatura de Servidor (2DAW). La idea era crear una aplicación para gestionar libros y después implementar tests para asegurar que todo funciona correctamente.

## 📚 Descripción del Proyecto

Aplicación Django donde los usuarios admin pueden registrar, editar y borrar libros, mientras que el resto de usuarios autenticados solo pueden ver los detalles. La aplicación tiene un modelo `Book` con campos como título, páginas, rating, estado de lectura, fechas y autores.

## 🔧 Bugs Encontrados Durante el Desarrollo

Durante la implementación de los tests encontré varios bugs que tuve que corregir:

### 1. Modelo Author sin max_length
Los campos `name` y `last_name` del modelo Author no tenían el parámetro `max_length` que es obligatorio en Django. Lo solucioné añadiendo `max_length=100` [code_file:12].

### 2. Validación de páginas incorrecta
El campo `pages` aceptaba valor 0, pero según las especificaciones el mínimo debe ser 1. Cambié el validador de `MinValueValidator(0)` a `MinValueValidator(1)` [code_file:12].

### 3. Validación de fechas al revés
La lógica para validar que `read_date` no sea anterior a `published_date` estaba invertida. Usaba `>` cuando tenía que usar `<` [code_file:12].

### 4. URLs sin el parámetro pk
Las rutas de editar, borrar y ver detalles no tenían el `<int:pk>` en la URL, así que Django no sabía qué libro mostrar. Añadí el parámetro a todas las rutas necesarias [code_file:13].

### 5. Permisos mal configurados
La vista de crear libro solo comprobaba que el usuario estuviera autenticado, pero debería comprobar que tiene permiso específico para crear. Cambié `LoginRequiredMixin` por `PermissionRequiredMixin` [code_file:14].

### 6. Mensajes de error genéricos
El formulario usaba los mensajes por defecto de Django en lugar de los personalizados. Tuve que añadir `error_messages` en la Meta class del formulario [code_file:11].

## ✅ Tests Implementados

He implementado **24 tests** en total, divididos en tres categorías:

### Tests del Modelo (6)
- Creación correcta de un libro básico
- Validación de páginas incorrectas
- Validación de rating fuera de rango (0 y 6)
- Validación de fecha de lectura anterior a publicación
- Libro con autor (relación ManyToMany)
- Libro con portada (FileField)

### Tests del Formulario (8)
- Formulario válido sin campos opcionales
- Título con más de 50 caracteres + verificar mensaje de error
- Título vacío + verificar mensaje de error
- Páginas incorrectas
- Rating incorrecto
- Fecha de lectura anterior + verificar mensaje de error
- Formulario con autor
- Formulario con portada

### Tests de Vistas (10)
Probé cada ruta con dos tipos de usuario: admin (con permisos) y regular (sin permisos):
- `/bookapp/form` - crear libro
- `/bookapp/list` - listar libros (accesible para todos)
- `/bookapp/<id>/edit` - editar libro
- `/bookapp/<id>/delete` - borrar libro
- `/bookapp/<id>/detail` - ver detalles (accesible para autenticados)

## 🚀 Cómo Ejecutar los Tests

Primero activa el entorno virtual:

source .venv/Scripts/activate  # Git Bash en Windows
# o
.venv\Scripts\Activate.ps1     # PowerShell

Luego ejecuta los tests:

bash
# Todos los tests
python manage.py test bookapp

# Por categoría
python manage.py test bookapp.tests.BookModelTest
python manage.py test bookapp.tests.BookFormTest
python manage.py test bookapp.tests.BookViewsTest

# Test específico
python manage.py test bookapp.tests.BookModelTest.test_book_creation_correct_without_author_and_cover

# 📊 Resultados
Los 24 tests se ejecutan en aproximadamente 12 segundos y todos pasan correctamente después de corregir los bugs mencionados [code_file:10].

# 📁 Estructura del Proyecto
text
bookproject/
├── manage.py
├── bookproject/
│   ├── settings.py
│   └── urls.py
└── bookapp/
    ├── models.py        # Modelo Book y Author
    ├── views.py         # Vistas CBV
    ├── urls.py          # Rutas de la app
    ├── forms.py         # BookForm con validaciones
    ├── tests.py         # Suite completa de tests
    └── templates/
        └── bookapp/
            ├── form.html
            ├── list.html
            ├── detail.html
            └── confirm_delete.html
# 💡 Lo que Aprendí
Importancia de escribir tests antes de considerar el código "terminado"

Los tests ayudan a encontrar bugs que a simple vista no se ven

Django tiene validaciones por defecto pero hay que personalizarlas bien

Es crucial probar los permisos de usuario para evitar accesos no autorizados

Los mensajes de error personalizados mejoran mucho la experiencia de usuario

# 🛠️ Tecnologías
Python 3.x

Django 4.x

SQLite (base de datos de tests)

Pillow (para manejo de imágenes)

## Autor: Antonio Barceló
## Curso: 2º Desarrollo de Aplicaciones Web (2DAW)
## Asignatura: Desarrollo Web en Entorno Servidor
