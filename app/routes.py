from multiprocessing.pool import AsyncResult
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from typing import Union
from app.tasks.celery_tasks import (
    send_telegram_message_task,
    create_tlogin_task,
    read_login_by_wallet_task,
    read_login_task,
)

# Define the router
status_router = APIRouter()
tlogin_router = APIRouter()
notification_router = APIRouter()
orderly_router = APIRouter()

@status_router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == 'PENDING':
        return {"status": "Pending"}
    elif task_result.state == 'SUCCESS':
        return {"status": "Success", "result": task_result.result}
    elif task_result.state == 'FAILURE':
        return {"status": "Failure", "result": str(task_result.result)}
    else:
        return {"status": task_result.state}

# Define the request body model
class NotificationRequest(BaseModel):
    token: int
    message: str


class TLoginCreateRequest(BaseModel):
    token: Union[str, int]
    wallet_address: str
    want_signal: bool

@notification_router.post("/send_notification")
async def send_notification(request: NotificationRequest):
    """
    Endpoint to send a trade notification via Telegram.

    Args:
        request (NotificationRequest): Contains the token (chat ID) and message.

    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        # Call the Celery task
        send_telegram_message_task.delay(request.token, request.message)
        return {"success": True, "message": "Notification sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending notification: {str(e)}")
    
@tlogin_router.post("/tlogin")
async def create_tlogin(request: TLoginCreateRequest):
    """
    Endpoint to create a TLogin entry.

    Args:
        tlogin (TLoginCreate): Contains the token, wallet address, and signal preference.

    Returns:
        dict: Status message indicating success or failure.
    """
    try:
        # Call the Celery task
        task = create_tlogin_task.delay(request.model_dump())
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating TLogin: {str(e)}")    


@tlogin_router.get("/tlogin/by_wallet/{wallet_address}")
async def read_login_by_wallet(wallet_address: str):
    """
    Endpoint to read a TLogin entry by wallet address.

    Args:
        wallet_address (str): The wallet address to look up.

    Returns:
        dict: The TLogin entry if found, otherwise an error message.
    """
    try:
        # Call the Celery task
        result = read_login_by_wallet_task.delay(wallet_address)
        return {"success": True, "data": result.get()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading TLogin by wallet: {str(e)}")
    
@tlogin_router.get("/tlogin/{token}")
async def read_login(token: str):
    """
    Endpoint to read a TLogin entry by token.

    Args:
        token (str): The token to look up.

    Returns:
        dict: The TLogin entry if found, otherwise an error message.
    """
    try:
        # Call the Celery task
        result = read_login_task.delay(token)
        return {"success": True, "data": result.get()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading TLogin by token: {str(e)}")