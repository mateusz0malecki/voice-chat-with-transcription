from celery import Celery

from settings import get_settings

app_settings = get_settings()

BROKER_URL = app_settings.celery_broker_url
BACKEND_URL = app_settings.celery_result_backend

app = Celery(
    'celery_worker',
    backend=BACKEND_URL,
    broker=BROKER_URL,
    include=['celery_worker.tasks']
)

if __name__ == '__main__':
    app.start()
