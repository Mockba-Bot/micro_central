from celery import Celery

celery_app = Celery(
    'micro_central',
    broker='redis://redis-micro-central:6379/0',
    backend='redis://redis-micro-central:6379/0',
    include=['app.tasks.notification_tasks']
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# if __name__ == '__main__':
#     celery_app.start()