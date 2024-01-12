from django.urls import path
from .views import subscriptions_categories


urlpatterns = [
    path('', subscriptions_categories, name='subscriptions_categories'),
    # написано subscriptions_categories на будущее, если буду добавлять подписку на автора
]