import logging
from datetime import timedelta

from django.utils import timezone

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from news.models import Post
from subscriptions.models import SubscriptionCategories

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
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


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            send_weekly_newsletter,
            trigger=CronTrigger(hour='18', minute='00', second='00', day_of_week='fri', timezone=settings.TIME_ZONE),
            # Каждую пятницу в 18:00
            id="send_weekly_newsletter",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_weekly_newsletter'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
