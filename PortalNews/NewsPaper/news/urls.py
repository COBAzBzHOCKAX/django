from django.urls import path
from django.views.decorators.cache import cache_page

from .views import PostsList, PostDetail, PostSearch, NewsCreate, ArticleCreate, PostUpdate, PostDelete, ArticleDetail

urlpatterns = [
    path('news/', cache_page(60)(PostsList.as_view()), name='posts'),

    # странички новостей
    path('news/<int:pk>/', cache_page(60*5)(PostDetail.as_view()), name='news_detail'),
    path('news/search/', PostSearch.as_view(), name='news_search'),
    path('news/create/', NewsCreate.as_view(), name='news_create'),
    path('news/<int:pk>/edit/', PostUpdate.as_view(), name='news_update'),
    path('news/<int:pk>/delete/', PostDelete.as_view(), name='news_delete'),

    # странички статей
    path('articles/<int:pk>/', cache_page(60*5)(ArticleDetail.as_view()), name='articles_detail'),
    path('articles/search/', PostSearch.as_view(), name='articles_search'),
    path('articles/create/', ArticleCreate.as_view(), name='articles_create'),
    path('articles/<int:pk>/edit/', PostUpdate.as_view(), name='articles_update'),
    path('articles/<int:pk>/delete/', PostDelete.as_view(), name='articles_delete'),
]