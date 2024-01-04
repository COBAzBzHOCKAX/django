from datetime import datetime

from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import *
from .filters import PostFilter
from .forms import NewsForm, ArticlesForm, UpdateForm

# Быстрые настройки страничек
PAGINATE_BY = 10  # Количество записей на странице


class PostsList(ListView):
    queryset = Post.objects.order_by('-date_of_creation')
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['random'] = '1234'
        return context


class PostDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(type_post='NWS')


class ArticleDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(type_post='ART')




class PostSearch(ListView):
    queryset = Post.objects.order_by('-date_of_creation')
    template_name = 'news/post_search.html'
    context_object_name = 'posts'
    paginate_by = PAGINATE_BY


    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        return context


class NewsCreate(CreateView):
    form_class = NewsForm
    model = Post
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = 'NWS'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('news_detail', kwargs={'pk': self.object.id})


class ArticleCreate(CreateView):
    form_class = ArticlesForm
    model = Post
    template_name = 'news/post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.type_post = 'ART'
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('articles_detail', kwargs={'pk': self.object.id})


class PostUpdate(UpdateView):
    form_class = UpdateForm
    model = Post
    template_name = 'news/post_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'news/post_delete.html'
    success_url = reverse_lazy('posts')