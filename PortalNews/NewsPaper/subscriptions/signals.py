from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from news.models import PostCategory
from .tasks import notifier


@receiver(m2m_changed, sender=PostCategory, weak=False)
def post_created(instance, **kwargs):
    if kwargs['action'] == 'post_add':
        notifier.delay(instance.pk)

