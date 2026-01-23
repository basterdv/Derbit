import logging
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from decouple import config

logger = logging.getLogger(__name__)

REDIS_BROKER_URL = config('REDIS_BROKER_URL')

app = Celery(
    'deribit_tracker',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BROKER_URL,
    include=['app.tasks']
)

# Конфигурация периодических задач (Celery Beat)
app.conf.beat_schedule = {
    'fetch-prices-every-minute': {
        'task': 'app.tasks.fetch_deribit_prices',
        'schedule': timedelta(seconds=60),
    },
}

app.conf.timezone = 'UTC'
