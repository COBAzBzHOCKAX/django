from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post


@receiver(post_save, sender=Post)
def post_created(instance, created, **kwargs):
    if not created:
        return

    emails = User.objects.filter(
        subscriptions__category__postcategory=instance.categories.category
    ).values_list('email', flat=True)

    subject = f'ПЕРВЫЙ новостной! В категории {instance.category} свежая новость/статья!'

    text_content = (
        f'{instance.title}\n'
        f"{(instance.text[:150] + '...') if len(instance.text) > 150 else instance.text}\n"
        f'Чиатать полностью на ПЕРВОМ новостном: http://127.0.0.1:8000{instance.get_absolut_url()}'
    )
    html_content = (
        f'{instance.title}<br.'
        f"{(instance.text[:150] + '...') if len(instance.text) > 150 else instance.text}<br>"
        f'Чиатать полностью на <a href="http://127.0.0.1:8000{instance.get_absolut_url()}">'
        f'ПЕРВОМ новостном</a>'
    )
    for email in emails:
        msg = EmailMultiAlternatives(subject, text_content, None, [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()