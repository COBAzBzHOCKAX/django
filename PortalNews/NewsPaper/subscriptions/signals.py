from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from news.models import PostCategory


@receiver(m2m_changed, sender=PostCategory, weak=False)
def post_created(instance, **kwargs):
    if kwargs['action'] == 'post_add':
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
            msg = EmailMultiAlternatives(subject, text_content, None, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
