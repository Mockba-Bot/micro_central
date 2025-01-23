from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TLogin
from app.schemas.TLoginSchema import TLogin as TLoginSchema, TLoginCreate
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.security import encrypt, decrypt
import os
import redis

# Initialize Redis connection
try:
    redis_client = redis.from_url(os.getenv("REDIS_URL"))
    redis_client.ping()
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")
    redis_client = None

router = APIRouter()

# Create a new TLogin
@router.post("/tlogin", response_model=TLoginSchema)
async def create_tlogin(tlogin: TLoginCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Encrypt sensitive fields
        new_tlogin = TLogin(
            token=tlogin.token,
            api_key=encrypt(tlogin.api_key),
            api_secret=encrypt(tlogin.api_secret),
            name=tlogin.name,
            last_name=tlogin.last_name,
            is_owner=tlogin.is_owner,
            want_signal=tlogin.want_signal,
            wallets=encrypt(tlogin.wallets) if tlogin.wallets else None,
            creation_date=tlogin.creation_date,
            end_subscription=tlogin.end_subscription
        )
        db.add(new_tlogin)
        await db.commit()
        await db.refresh(new_tlogin)
        return new_tlogin
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Retrieve a TLogin by token
@router.get("/tlogin/{token}", response_model=TLoginSchema)
async def read_login(token: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TLogin).where(TLogin.token == token))
    login = result.scalar_one_or_none()
    if login is None:
        raise HTTPException(status_code=404, detail="Login not found")

    # Decrypt sensitive fields
    login.api_key = login.api_key
    login.api_secret = login.api_secret
    login.wallets = login.wallets if login.wallets else None

    return login

@router.get("/tlogin/verify/{token}")
async def verify_login(token: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TLogin).where(TLogin.token == token))
    login = result.scalar_one_or_none()
    if login is None:
        return {"exists": False}
    return {"exists": True}    

# Update a TLogin by token
@router.put("/tlogin/{token}", response_model=TLoginSchema)
async def update_tlogin(token: int, tlogin: TLoginSchema, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TLogin).filter(TLogin.token == token))
        existing_tlogin = result.scalars().first()
        if not existing_tlogin:
            raise HTTPException(status_code=404, detail="TLogin not found")

        # Update fields with encrypted data
        existing_tlogin.api_key = encrypt(tlogin.api_key)
        existing_tlogin.api_secret = encrypt(tlogin.api_secret)
        existing_tlogin.name = tlogin.name
        existing_tlogin.last_name = tlogin.last_name
        existing_tlogin.is_owner = tlogin.is_owner
        existing_tlogin.want_signal = tlogin.want_signal
        existing_tlogin.wallets = encrypt(tlogin.wallets) if tlogin.wallets else None
        existing_tlogin.creation_date = tlogin.creation_date
        existing_tlogin.end_subscription = tlogin.end_subscription

        await db.commit()

        # Remove the Redis cache for the updated user
        redis_client.delete(f"user_data:{token}")

        await db.refresh(existing_tlogin)
        return existing_tlogin
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

