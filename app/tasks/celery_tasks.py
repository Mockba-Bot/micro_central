import logging
from app.tasks.celery_app import celery_app
from app.utils.send_bot_notification import send_telegram_message
from app.utils.getHistorical import  get_historical_data

logger = logging.getLogger(__name__)

@celery_app.task
def send_telegram_message_task(token, message):
    logger.info(f"Sending telegram message to {token}")
    send_telegram_message(token, message)

@celery_app.task
def get_historical_data_task(pair, timeframe, values):
    logger.info(f"Getting historical data for {pair} with timeframe {timeframe} and values {values}")
    df = get_historical_data(pair, timeframe, values)
    return df.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries