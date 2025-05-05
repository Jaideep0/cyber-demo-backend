import os
from celery import Celery

# Read Redis URL from env
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Instantiate the Celery app
celery = Celery(
    "cyber_demo",
    broker=redis_url,
    backend=redis_url
)

# Load the rest of the config from celeryconfig.py
celery.config_from_object("celeryconfig")

# Auto-discover tasks in the app.tasks module
celery.autodiscover_tasks(["app.tasks"])
