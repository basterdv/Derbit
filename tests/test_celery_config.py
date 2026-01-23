from datetime import timedelta
from unittest.mock import patch
import pytest
from app.celery_app import app
from decouple import config

REDIS_BROKER_URL = config('REDIS_BROKER_URL')


def test_celery_broker_url_is_configured():
    broker_url = app.conf.broker_url

    # Assert
    # Проверяем, что URL брокера не пустой и содержит ожидаемый протокол Redis
    assert broker_url is not None
    assert broker_url.startswith(REDIS_BROKER_URL)


def test_celery_config_values():
    """
    Проверяем, что Celery инициализирован с корректными базовыми настройками.
    """
    # Проверка брокера (должен быть redis согласно вашему коду)
    assert "redis" in app.conf.broker_url

    # Проверка часового пояса
    assert app.conf.timezone == 'UTC'


def test_beat_schedule_structure():
    """
    Проверяем, что периодическая задача зарегистрирована правильно.
    """
    schedule = app.conf.beat_schedule
    task_key = 'fetch-prices-every-minute'

    # Проверяем наличие ключа в расписании
    assert task_key in schedule

    # Проверяем параметры задачи
    task_data = schedule[task_key]
    assert task_data['task'] == 'app.tasks.fetch_deribit_prices'
    assert task_data['schedule'] == timedelta(seconds=60)


def test_app_include_modules():
    """
    Проверяем, что модули с задачами включены в приложение.
    """
    assert 'app.tasks' in app.conf.include
