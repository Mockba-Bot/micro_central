from multiprocessing.pool import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from app.tasks.celery_app import celery_app
from typing import Union
from app.tasks.celery_tasks import (
    send_telegram_message_task
)
from app.controllers.TLoginController import create_tlogin, read_login_by_wallet, read_login
from app.database import get_db

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
    language: str = "en"

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
async def create_tlogin_route(request: TLoginCreateRequest, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to create a TLogin entry and return a signed JWT token.

    Args:
        request (TLoginCreateRequest): Contains the token, wallet address, and signal preference.

    Returns:
        dict: JWT token, expiration info, and user preferences.
    """
    try:
        return await create_tlogin(request, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating TLogin: {str(e)}")  


@tlogin_router.get("/tlogin/by_wallet/{wallet_address}")
async def read_login_by_wallet_route(wallet_address: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to read a TLogin entry by wallet address.

    Args:
        wallet_address (str): The wallet address to look up.

    Returns:
        dict: The TLogin entry with JWT if found.
    """
    try:
        return await read_login_by_wallet(wallet_address, db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading TLogin by wallet: {str(e)}")
    
@tlogin_router.get("/tlogin/validate/{token}", include_in_schema=False)
async def validate_token_route(token: str, db: AsyncSession = Depends(get_db)):
    """
    Fast lightweight endpoint to validate JWT token for NGINX auth_request.
    It reuses the full logic from `read_login()` but returns only 200/403/404.
    """
    try:
        await read_login(token, db=db)  # ← reuse your JWT logic
        return Response(status_code=200)  # ✅ Valid token
    except HTTPException as e:
        if e.status_code in (403, 404):
            raise e  # ❌ Invalid token or not found
        raise HTTPException(status_code=500, detail="Internal validation error")