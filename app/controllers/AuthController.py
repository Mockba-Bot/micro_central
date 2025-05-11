from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
import jwt
from eth_account.messages import defunct_hash_message
from eth_account import Account
import os
from pydantic import BaseModel
from typing import Set, Optional

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET")
active_tokens: Set[str] = set()  # In-memory token store (use Redis in production)

class LoginRequest(BaseModel):
    message: str
    signature: str
    wallet_address: str

class ManualLoginRequest(BaseModel):
    user_id: str

def generate_token(payload: dict) -> str:
    """Generate session token without expiration"""
    payload.update({
        "iat": datetime.now(timezone.utc),
        "jti": os.urandom(16).hex()  # Unique token identifier
    })
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    active_tokens.add(token)  # Track active tokens
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify token is valid and active"""
    try:
        if token not in active_tokens:
            return None
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None

def verify_metamask_signature(wallet_address: str, signature: str, message: str) -> bool:
    """Verify MetaMask signature"""
    try:
        message_hash = defunct_hash_message(text=message)
        recovered_address = Account.recover_message(message_hash, signature=signature)
        return recovered_address.lower() == wallet_address.lower()
    except:
        return False

@router.post("/auth/wallet-login")
async def wallet_login(request: LoginRequest):
    """Authenticate using MetaMask signature"""
    if not verify_metamask_signature(
        request.wallet_address,
        request.signature,
        request.message
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    token = generate_token({"wallet_address": request.wallet_address.lower()})
    return {"token": token}

@router.post("/auth/manual-login")
async def manual_login(request: ManualLoginRequest):
    """Manual login for testing (bypasses MetaMask)"""
    if not request.user_id:
        raise HTTPException(status_code=400, detail="User ID required")
    
    token = generate_token({"user_id": request.user_id})
    return {"token": token}

@router.post("/auth/logout")
async def logout(authorization: HTTPAuthorizationCredentials = Depends(security)):
    """Remove token from active sessions"""
    token = authorization.credentials
    if token in active_tokens:
        active_tokens.remove(token)
    return {"success": True}

@router.get("/auth/verify")
async def verify_token(auth: HTTPAuthorizationCredentials = Depends(security)):
    """Verify token validity"""
    payload = verify_token(auth.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Return different fields based on login method
    response = {"valid": True}
    if "wallet_address" in payload:
        response["wallet"] = payload["wallet_address"]
    if "user_id" in payload:
        response["user_id"] = payload["user_id"]
    
    return response