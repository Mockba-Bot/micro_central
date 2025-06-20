from fastapi import APIRouter, Depends, HTTPException, Request
from jose import JWTError
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
import os
from datetime import datetime, timezone
import time
import jwt

from fastapi import FastAPI

creation_date=datetime.now(timezone.utc)

app = FastAPI()
redis_client = None

SECRET_KEY = os.getenv("JWT_SECRET")
JWT_EXPIRATION = 3 * 24 * 60 * 60  # 3 days = 259200 seconds

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

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
    """
    Validate the hash from Telegram to ensure data is authentic.
    """
    # Make a copy of the data to avoid modifying the original
    data_check = data.copy()
    hash_str = data_check.pop("hash", None)
    
    if not hash_str:
        return False
        
    # Telegram requires specific field ordering and string formatting
    data_check_str = "\n".join(
        f"{k}={v}" 
        for k, v in sorted(data_check.items())
    )

    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(
        secret_key, 
        msg=data_check_str.encode(), 
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(computed_hash, hash_str)


async def create_tlogin_entry(tlogin: TLoginCreate, db: AsyncSession) -> TLogin:
    result = await db.execute(
        select(TLogin).where(TLogin.token == int(tlogin.token))
    )
    existing = result.scalar_one_or_none()

    if existing:
        return existing

    user = TLogin(
        token=tlogin.token,
        wallet_address=tlogin.wallet_address,
        want_signal=tlogin.want_signal,
        language=tlogin.language,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user

# Create a new TLogin
# @router.post("/tlogin", response_model=TLoginSchema)
async def create_tlogin(tlogin: TLoginCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await create_tlogin_entry(tlogin, db)

        payload = {
            "telegram_id": str(user.token),
            "wallet_address": user.wallet_address,
            "exp": int(time.time()) + JWT_EXPIRATION,
        }
        jwt_token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return {
            "status": "ok",
            "data": {
                "token": jwt_token,
                "expires_at": JWT_EXPIRATION,
                "wallet_address": user.wallet_address,
                "want_signal": user.want_signal,
                "language": user.language,
                "creation_date": user.creation_date.isoformat() if user.creation_date else None,
            },
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ✅ Reusable response builder (same as in create_tlogin)
def build_login_response(user: TLogin):
    payload = {
        "telegram_id": str(user.token),
        "wallet_address": user.wallet_address,
        "exp": int(time.time()) + JWT_EXPIRATION,
    }
    jwt_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "status": "ok",
        "data": {
            "token": jwt_token,
            "expires_at": JWT_EXPIRATION,
            "wallet_address": user.wallet_address,
            "want_signal": user.want_signal,
            "language": user.language,
            "creation_date": user.creation_date.isoformat() if user.creation_date else None,
        },
    }

# Retrieve a TLogin by wallet address
# @router.get("/tlogin/by_wallet/{wallet_address}", response_model=TLoginSchema)
async def read_login_by_wallet(wallet_address: str, db: AsyncSession = Depends(get_db)):
    redis_client = await get_redis()

    # Try Redis cache
    if redis_client:
        cached_login = await redis_client.get(f"user_data_wallet:{wallet_address}")
        if cached_login:
            try:
                user = TLogin.model_validate_json(cached_login)
            except Exception:
                user = None
            else:
                return build_login_response(user)

    # Fetch from DB
    result = await db.execute(select(TLogin).where(TLogin.wallet_address == wallet_address))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="Login not found")

    # Cache in Redis
    if redis_client:
        await redis_client.set(f"user_data_wallet:{wallet_address}", user.json(), ex=JWT_EXPIRATION)

    return build_login_response(user)


# Retrieve a TLogin by token
# @router.get("/tlogin/{token}", response_model=TLoginSchema)
async def read_login(token: str, db: AsyncSession = Depends(get_db)):
    # Step 1 – Decode JWT
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        telegram_id = int(payload.get("telegram_id"))
        wallet_address = payload.get("wallet_address")
        if telegram_id is None or wallet_address is None:
            raise HTTPException(status_code=403, detail="Invalid JWT structure")
    except JWTError as e:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Step 2 – Redis Cache Check
    redis_client = await get_redis()
    if redis_client:
        cache_key = f"user_data:{token}"
        cached = await redis_client.get(cache_key)
        if cached:
            try:
                return TLoginSchema.model_validate_json(cached.decode("utf-8"))
            except Exception:
                pass  # fallback to DB

    # Step 3 – Fetch from DB
    result = await db.execute(
        select(TLogin).where(
            TLogin.token == telegram_id,
            TLogin.wallet_address == wallet_address
        )
    )
    login = result.scalar_one_or_none()
    if not login:
        raise HTTPException(status_code=404, detail="Login not found")

    # Step 4 – Cache the result
    if redis_client:
        await redis_client.set(f"user_data:{token}", login.json(), ex=60 * 60 * 3)  # 3 hours

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

