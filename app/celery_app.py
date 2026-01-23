from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
import os

# Используем переменные окружения для конфигурации Redis
# Например, REDIS_BROKER_URL="redis://redis:6379/0"
# REDIS_BROKER_URL = os.getenv("REDIS_BROKER_URL", "redis://localhost:6379/0")
REDIS_BROKER_URL = "redis://127.0.0.1:6379/0"

app = Celery(
    'deribit_tracker',
    broker=REDIS_BROKER_URL,
    backend=REDIS_BROKER_URL,
    include=['app.tasks'] # Указывает Celery, где искать задачи (@app.task)
)

# Конфигурация периодических задач (Celery Beat)
app.conf.beat_schedule = {
    # Задача будет запускаться каждую минуту
    'fetch-prices-every-minute': {
        'task': 'app.tasks.fetch_deribit_prices',
        # 'schedule': crontab(minute='*'),
        'schedule': timedelta(seconds=60), # Альтернатива для 60 секунд
    },
}
app.conf.timezone = 'UTC' # Убедитесь, что часовой пояс согласован
