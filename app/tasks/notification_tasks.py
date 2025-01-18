from app.tasks.celery_app import celery_app
from app.utils.send_bot_notification import send_telegram_message

@celery_app.task
def send_telegram_message_task(token, message):
    send_telegram_message(token, message)