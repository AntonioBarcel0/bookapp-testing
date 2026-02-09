from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q, Avg, Max, Min, Count
from bookapp.forms import BookForm
from bookapp.models import Book
import json

class BookCreate(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookList(ListView):
    model = Book
    context_object_name = 'books'
    template_name = 'bookapp/list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        order = self.request.GET.get('order')
        
        if search:
            queryset = queryset.filter(Q(title__icontains=search))
        
        if order:
            queryset = queryset.order_by(order)
        
        return queryset

class BookUpdate(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'bookapp/form.html'
    success_url = reverse_lazy('book_list')

class BookDelete(LoginRequiredMixin, DeleteView):
    model = Book
    template_name = 'bookapp/confirm_delete.html'
    success_url = reverse_lazy('book_list')

class BookDetail(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'bookapp/detail.html'
    context_object_name = 'book'

class BookStats(ListView):
    model = Book
    template_name = 'bookapp/stats.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['max_pages_book'] = Book.objects.order_by('-pages').first()
        context['min_pages_book'] = Book.objects.order_by('pages').first()
        
        stats = Book.objects.aggregate(
            avg_pages=Avg('pages'),
            avg_rating=Avg('rating')
        )
        context['avg_pages'] = stats['avg_pages'] or 0
        context['avg_rating'] = stats['avg_rating'] or 0
        
        status_data = Book.objects.values('status').annotate(count=Count('id')).order_by('status')
        status_dict = {item['status']: item['count'] for item in status_data}
        
        status_choices = dict(Book.STATUS_CHOICES)
        status_labels = []
        status_values = []
        for code, label in Book.STATUS_CHOICES:
            status_labels.append(label)
            status_values.append(status_dict.get(code, 0))
        
        context['status_labels'] = json.dumps(status_labels)
        context['status_values'] = json.dumps(status_values)
        
        rating_data = Book.objects.filter(rating__isnull=False).values('rating').annotate(count=Count('id')).order_by('rating')
        rating_dict = {item['rating']: item['count'] for item in rating_data}
        
        rating_labels = []
        rating_values = []
        for i in range(1, 6):
            rating_labels.append(str(i))
            rating_values.append(rating_dict.get(i, 0))
        
        context['rating_labels'] = json.dumps(rating_labels)
        context['rating_values'] = json.dumps(rating_values)
        
        return context

def register(request):
    form = UserCreationForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        return redirect('book_list')
    return render(request, 'bookapp/form.html', {'form': form})
