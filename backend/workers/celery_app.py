"""Celery application configuration."""

import asyncio
import os

from celery import Celery

from config.settings import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "survey_simulation",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.simulation_tasks"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)

# Result expiration
celery_app.conf.result_expires = 86400  # 24 hours


def get_event_loop():
    """Get or create event loop for async operations."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
