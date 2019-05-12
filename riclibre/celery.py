from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# Default django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'riclibre.settings')

app = Celery('riclibre', broker=os.getenv('BROKER_URL', 'redis://localhost:6379'))

# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object('django.conf:settings', namespace='CELERY')



app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request}')
