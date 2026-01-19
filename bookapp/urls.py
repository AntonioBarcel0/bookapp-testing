from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from bookapp import views

urlpatterns = [
    path('form', views.form, name='form'),
    path('list', views.MovieList.as_view(), name='book_list'),
    path('<int:pk>/edit', views.MovieUpdate.as_view(), name='book_edit'),
    path('<int:pk>/delete', views.MovieDelete.as_view(), name='book_delete'),
    path('<int:pk>/detail', views.MovieDetail.as_view(), name='book_detail'),
    path('register', views.register, name='register'),
    path('login', LoginView.as_view(template_name = 'bookapp/form.html', redirect_authenticated_user = True), name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]