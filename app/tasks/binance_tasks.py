from app.tasks.celery_app import celery_app
from app.utils.getHistorical import get_all_binance, get_historical_data

@celery_app.task
def get_all_binance_task(token, message):
    get_all_binance(token, message)

@celery_app.task
def get_historical_data_task(pair, timeframe, values):
    get_historical_data(pair, timeframe, values)    