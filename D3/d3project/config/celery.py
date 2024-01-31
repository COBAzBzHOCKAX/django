import os

from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('d3project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_shedule = {
    'print_every_5_seconds': {
        'task': 'simpleapp.tasks.printer',
        'schedule': 5,
        'args': (5,),
    }
}