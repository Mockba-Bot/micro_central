import logging
from app.tasks.celery_app import celery_app
from app.utils.send_bot_notification import send_telegram_message

logger = logging.getLogger(__name__)

@celery_app.task(queue="central")
def send_telegram_message_task(token, message):
    logger.info(f"Sending telegram message to {token}")
    send_telegram_message(token, message)