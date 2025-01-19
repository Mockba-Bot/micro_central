from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.tasks.celery_tasks import send_telegram_message_task

# Define the router
router = APIRouter()

# Define the request body model
class NotificationRequest(BaseModel):
    token: str
    message: str

@router.post("/send_notification")
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
