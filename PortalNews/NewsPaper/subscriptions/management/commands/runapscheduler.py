import logging
from datetime import timedelta, timezone, datetime

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from news.models import Category, Post
from subscriptions.models import SubscriptionCategories

logger = logging.getLogger(__name__)


def send_weekly_newsletter():
    now = datetime.now()
    last_week_start = now - timedelta(days=now.weekday() + 7)
    last_week_end = now - timedelta(days=now.weekday() + 1)

    subscriptions = SubscriptionCategories.objects.all()

    unique_posts_by_category = {}

    for subscription in subscriptions:
        user = subscription.user
        categories = Category.objects.filter(subscriptions=subscription)

        news_by_category = {}
        for category in categories:
            # Получаем все посты за прошедшую неделю для каждой категории
            posts = Post.objects.filter(
                categories__category=category,
                date_of_creation__range=[last_week_start, last_week_end]
            ).distinct()  # получаем уникальный список постов

            unique_posts_by_category.update({post.id: post for post in posts})

    if unique_posts_by_category:
        subject = 'ПЕРВЫЙ новостной | Новости и статьи за прошедшую неделю по вашим подпискам'
        from_email = None
        to_email = [user.email]

        unique_posts = list(unique_posts_by_category.values())

        unique_posts.sort(key=lambda x: x.date_of_creation, reverse=True)

        text_content = render_to_string('subscriptions/weekly_newsletter_email.txt', {'unique_posts': unique_posts})
        html_content = render_to_string('subscriptions/weekly_newsletter_email.html', {'unique_posts': unique_posts})

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
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
            # trigger=CronTrigger(second="0 18 * * 4"),  # Каждую пятницу в 18:00
            trigger=CronTrigger(second="*/10"),
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

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