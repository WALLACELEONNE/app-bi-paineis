from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "bi_agro",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.importacao", "app.tasks.exportacao", "app.tasks.manutencao"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,
    task_soft_time_limit=3300,
    task_default_queue="default",
    task_queues={
        "default": {"exchange": "default", "routing_key": "default"},
        "importacao": {"exchange": "importacao", "routing_key": "importacao"},
        "exportacao": {"exchange": "exportacao", "routing_key": "exportacao"},
    },
    task_routes={
        "app.tasks.importacao.*": {"queue": "importacao"},
        "app.tasks.exportacao.*": {"queue": "exportacao"},
    },
)
