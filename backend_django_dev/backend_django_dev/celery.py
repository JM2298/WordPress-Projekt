import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend_django_dev.settings")

app = Celery("backend_django_dev")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
