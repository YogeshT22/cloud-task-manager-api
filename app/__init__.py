# app/__init__.py
# Import celery_app to ensure it's available for autodiscovery
from .celery_app import celery_app

__all__ = ["celery_app"]
