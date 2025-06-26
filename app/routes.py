from multiprocessing.pool import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from celery.result import AsyncResult
from typing import Union
from app.controllers.TLoginController import create_tlogin, read_login_by_wallet, read_login
from app.database import get_db

# Define the router
status_router = APIRouter()
tlogin_router = APIRouter()
orderly_router = APIRouter()


class TLoginCreateRequest(BaseModel):
    token: Union[str, int]
    wallet_address: str
    want_signal: bool
    language: str = "en"

    
    
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
    """
    try:
        return await read_login_by_wallet(wallet_address, db)
    except HTTPException as e:
        raise e  # ✅ re-raise cleanly without turning into 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    
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