from fastapi import APIRouter, Depends, HTTPException, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta, timezone
import jwt
from eth_account.messages import defunct_hash_message
from eth_account import Account
from typing import Dict, Optional
import os
from pydantic import BaseModel

router = APIRouter()
security = HTTPBearer()

# Session store for refresh tokens (in production, use Redis instead)
active_sessions: Dict[str, dict] = {}

# Models
class LoginRequest(BaseModel):
    message: str
    signature: str
    wallet_address: str

class ManualLoginRequest(BaseModel):
    user_id: str

class RefreshRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
REFRESH_SECRET = JWT_SECRET + "-refresh"

def generate_token(payload: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")

def generate_refresh_token(payload: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, REFRESH_SECRET, algorithm="HS256")

def verify_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def verify_refresh_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, REFRESH_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def verify_metamask_signature(wallet_address: str, signature: str, message: str) -> bool:
    try:
        message_hash = defunct_hash_message(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except:
        return False

@router.post("/auth/wallet-login")
async def wallet_login(request: LoginRequest):
    """Authenticate using MetaMask signature with JWT and refresh token"""
    if not verify_metamask_signature(
        request.wallet_address,
        request.signature,
        request.message
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = {"wallet_address": request.wallet_address.lower()}
    token = generate_token(payload)
    refresh_token = generate_refresh_token(payload)
    
    # Store refresh token (in production, use Redis with expiration)
    active_sessions[refresh_token] = {
        "wallet_address": request.wallet_address.lower(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).timestamp()
    }
    
    return {
        "token": token,
        "refresh_token": refresh_token,
        "expires_in": 3600
    }

@router.post("/auth/manual-login")
async def manual_login(request: ManualLoginRequest):
    """Manual login for testing with JWT and refresh token"""
    payload = {"user_id": request.user_id}
    token = generate_token(payload)
    refresh_token = generate_refresh_token(payload)
    
    active_sessions[refresh_token] = {
        "user_id": request.user_id,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).timestamp()
    }
    
    return {
        "token": token,
        "refresh_token": refresh_token,
        "expires_in": 3600
    }

@router.post("/auth/refresh")
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token"""
    if not request.refresh_token or request.refresh_token not in active_sessions:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    session = active_sessions[request.refresh_token]
    if datetime.now(timezone.utc).timestamp() > session["expires_at"]:
        del active_sessions[request.refresh_token]
        raise HTTPException(status_code=401, detail="Refresh token expired")
    
    # Verify the refresh token structure
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        del active_sessions[request.refresh_token]
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Generate new tokens
    new_token = generate_token(session)
    new_refresh_token = generate_refresh_token(session)
    
    # Update session
    del active_sessions[request.refresh_token]
    active_sessions[new_refresh_token] = {
        **session,
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=7)).timestamp()
    }
    
    return {
        "token": new_token,
        "refresh_token": new_refresh_token,
        "expires_in": 3600
    }

@router.post("/auth/logout")
async def logout(request: LogoutRequest):
    """Invalidate refresh token"""
    if request.refresh_token in active_sessions:
        del active_sessions[request.refresh_token]
    return {"success": True}

@router.get("/auth/verify")
async def verify_token(authorization: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token validity"""
    token = authorization.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {
        "valid": True,
        "user": payload.get("user_id"),
        "wallet": payload.get("wallet_address")
    }