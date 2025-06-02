from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TLogin
from app.schemas.TLoginSchema import TLogin as TLoginSchema, TLoginCreate
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
import os
from redis import asyncio as aioredis
import hmac
import hashlib
from datetime import datetime, timezone

from fastapi import FastAPI

creation_date=datetime.now(timezone.utc)

app = FastAPI()
redis_client = None

async def startup_event():
    global redis_client
    try:
        redis_client = aioredis.from_url(os.getenv("REDIS_URL"))
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection error: {e}")
        redis_client = None

async def get_redis():
    return redis_client

router = APIRouter()

def verify_telegram_hash(data: dict, bot_token: str) -> bool:
    auth_data = data.copy()
    hash_to_check = auth_data.pop("hash")
    data_check_arr = [f"{k}={v}" for k, v in sorted(auth_data.items())]
    data_check_string = "\n".join(data_check_arr)
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return computed_hash == hash_to_check

# Create a new TLogin
@router.post("/tlogin", response_model=TLoginSchema)
async def create_tlogin(tlogin: TLoginCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Encrypt sensitive fields
        new_tlogin = TLogin(
            token=tlogin.token,
            wallet_address=tlogin.wallet_address,
            want_signal=tlogin.want_signal,
            language=tlogin.language
        )
        db.add(new_tlogin)
        await db.commit()
        await db.refresh(new_tlogin)
        return new_tlogin
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Retrieve a TLogin by wallet address
@router.get("/tlogin/by_wallet/{wallet_address}", response_model=TLoginSchema)
async def read_login_by_wallet(wallet_address: str, db: AsyncSession = Depends(get_db)):
    redis_client = await get_redis()
    if redis_client:
        cached_login = await redis_client.get(f"user_data_wallet:{wallet_address}")
        if cached_login:
            try:
                cached_login = cached_login.decode("utf-8")
                return TLoginSchema.model_validate_json(cached_login)
            except UnicodeDecodeError:
                return TLoginSchema.model_validate_json(cached_login)

    result = await db.execute(select(TLogin).where(TLogin.wallet_address == wallet_address))
    login = result.scalar_one_or_none()
    if login is None:
        raise HTTPException(status_code=404, detail="Login not found")

    if redis_client:
        await redis_client.set(f"user_data_wallet:{wallet_address}", login.json())

    return login


# Retrieve a TLogin by token
@router.get("/tlogin/{token}", response_model=TLoginSchema)
async def read_login(token: int, db: AsyncSession = Depends(get_db)):
    # Get Redis client
    redis_client = await get_redis()
    if redis_client:
        # Check Redis cache first
        cached_login = await redis_client.get(f"user_data:{token}")
        if cached_login:
            try:
                # Try to decode as UTF-8 first
                cached_login = cached_login.decode("utf-8")
                return TLoginSchema.model_validate_json(cached_login)
            except UnicodeDecodeError:
                # If UTF-8 fails, try to parse directly from bytes
                return TLoginSchema.model_validate_json(cached_login)

    # If not in cache, fetch from database
    result = await db.execute(select(TLogin).where(TLogin.token == token))
    login = result.scalar_one_or_none()
    if login is None:
        raise HTTPException(status_code=404, detail="Login not found")

    # Cache the result in Redis if available
    if redis_client:
        await redis_client.set(f"user_data:{token}", login.json())

    return login


# # Update a TLogin by token
# @router.put("/tlogin/{token}", response_model=TLoginSchema)
# async def update_tlogin(token: int, tlogin: TLoginCreate, db: AsyncSession = Depends(get_db)):
#     try:
#         result = await db.execute(select(TLogin).filter(TLogin.token == token))
#         existing_tlogin = result.scalars().first()
#         if not existing_tlogin:
#             raise HTTPException(status_code=404, detail="TLogin not found")

#         # Update fields with encrypted data
#         existing_tlogin.want_signal = tlogin.want_signal
#         existing_tlogin.language = tlogin.language

#         await db.commit()

#         # Remove the Redis cache for the updated user
#         redis_client = await get_redis()
#         if redis_client:
#             await redis_client.delete(f"user_data:{token}")

#         await db.refresh(existing_tlogin)
#         return existing_tlogin
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/telegram")
async def handle_telegram_auth(request: Request):
    data = await request.json()
    bot_token = os.getenv("API_TOKEN")  # Replace with your bot's token
    
    # 1. Verify the hash (critical for security)
    if not verify_telegram_hash(data, bot_token):
        raise HTTPException(status_code=401, detail="Invalid Telegram hash")
    
    # 2. Extract Telegram ID
    telegram_id = data["telegram_id"]
    
    # 3. Store in DB or process further (your logic here)
    return {"status": "success", "telegram_id": telegram_id}

