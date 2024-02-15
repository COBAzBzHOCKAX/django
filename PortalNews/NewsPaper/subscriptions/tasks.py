from datetime import timedelta

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from config import settings
from news.models import Post
from subscriptions.models import SubscriptionCategories


@shared_task
def notifier(arg_id):
    instance = Post.objects.get(id=arg_id)
    emails = User.objects.filter(
        subscriptions__category__in=instance.categories.all()
    ).values_list('email', flat=True)
    emails = set(emails)
    categories_post = ', '.join([cat.category for cat in instance.categories.all()])
    subject = f'ПЕРВЫЙ новостной! В категориях {categories_post} свежая новость/статья!'

    text_content = (
        f'{instance.title}\n'
        f"{(instance.text[:150] + '...') if len(instance.text) > 150 else instance.text}\n"
        f'Чиатать полностью на ПЕРВОМ новостном: http://127.0.0.1:8000{instance.get_absolute_url()}'
    )
    html_content = (
        f'{instance.title}<br.'
        f"{(instance.text[:150] + '...') if len(instance.text) > 150 else instance.text}<br>"
        f'Чиатать полностью на <a href="http://127.0.0.1:8000{instance.get_absolute_url()}">'
        f'ПЕРВОМ новостном</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


@shared_task
def send_weekly_digest():
    today = timezone.now()
    last_week = today - timedelta(days=7)
    posts = Post.objects.filter(date_of_creation__gte=last_week).order_by('-date_of_creation')
    categories = set(posts.values_list('categories__id', flat=True))
    subscribers_emails = set(
        SubscriptionCategories.objects.filter(category__id__in=categories).values_list('user__email', flat=True)
    )

    for subscriber_email in subscribers_emails:
        subscriptions_to_categories = SubscriptionCategories.objects.filter(user__email=subscriber_email)
        list_subscriptions_to_categories = set(subscriptions_to_categories.values_list('category', flat=True))
        # Посты без повторов для пользователя, соответствующий подпискам на категории
        subscribed_posts = posts.filter(postcategory__category__in=list_subscriptions_to_categories).distinct()


        subject = 'ПЕРВЫЙ новостной | Новости и статьи за прошедшую неделю по вашим подпискам'
        from_email = None
        to_email = subscriber_email

        text_content = render_to_string(
            'subscriptions/weekly_newsletter_email.txt',
            {'subscribed_posts': subscribed_posts, 'link': settings.SITE_URL}
        )
        html_content = render_to_string(
            'subscriptions/weekly_newsletter_email.html',
            {'subscribed_posts': subscribed_posts, 'link': settings.SITE_URL}
        )

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, 'text/html')
        msg.send()