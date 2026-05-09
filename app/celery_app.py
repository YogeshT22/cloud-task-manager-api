# app/celery_app.py
"""
Celery configuration and initialization with RabbitMQ as the broker.
"""

from celery import Celery
import os
import logging


logger = logging.getLogger(__name__)


# RabbitMQ broker and RPC result backend configuration
CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "rpc://")

# Initialize Celery app with explicit configuration
celery_app = Celery(
    "task_manager",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
)

# Celery configuration with optimizations and retry settings
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task tracking and timeouts
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Result backend
    result_expires=3600,

    # Connection and broker settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_heartbeat=30,
    broker_pool_limit=10,

    # Task processing
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# Auto-discover tasks from all installed apps
celery_app.autodiscover_tasks(["app"])


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery."""
    print(f'Request: {self.request!r}')
