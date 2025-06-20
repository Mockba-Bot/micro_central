from celery import shared_task
import logging
import asyncio
from app.utils.send_bot_notification import send_telegram_message
from app.controllers.TLoginController import (
    create_tlogin,
    read_login_by_wallet,
    read_login
)
from app.database import AsyncSessionLocal
from app.schemas.TLoginSchema import TLoginCreate, TLogin as TLoginSchema

logger = logging.getLogger(__name__)


@shared_task(queue="central")
def send_telegram_message_task(token, message):
    return send_telegram_message(token, message)


@shared_task(queue="central")
def create_tlogin_task(tlogin_data):
    if isinstance(tlogin_data.get('token'), str):
        tlogin_data['token'] = int(tlogin_data['token'])

    tlogin = TLoginCreate(**tlogin_data)

    async def _create():
        async with AsyncSessionLocal() as db:
            login = await create_tlogin(tlogin, db=db)
            return TLoginSchema.model_validate(login).model_dump()

    return run_async(_create)


@shared_task(queue="central")
def read_login_by_wallet_task(wallet_address):
    async def _read():
        async with AsyncSessionLocal() as db:
            login = await read_login_by_wallet(wallet_address, db=db)
            return TLoginSchema.model_validate(login).model_dump()

    return run_async(_read)


@shared_task(queue="central")
def read_login_task(token):
    async def _read():
        async with AsyncSessionLocal() as db:
            login = await read_login(token, db=db)
            return TLoginSchema.model_validate(login).model_dump()

    return run_async(_read)


def run_async(async_func):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(async_func())
