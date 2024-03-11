from app.config import settings
from celery import Celery
from celery.schedules import crontab


app_celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    include=["app.tasks.tasks", "app.tasks.scheduled"]
)

app_celery.conf.beat_schedule = {
    "parser-task": {
        "task": "periodic_parser",
        "schedule": 60*60
    }
}