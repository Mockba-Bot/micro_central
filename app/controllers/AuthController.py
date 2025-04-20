from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from datetime import datetime, timezone
from app.utils.security import (
    create_jwt_token,
    verify_jwt_token,
    verify_metamask_signature
)
from app.models.TLogin import TLogin
from app.schemas.TLoginSchema import LoginRequest, ManualLoginRequest
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

@router.post("/auth/login")
async def login_with_metamask(request: LoginRequest):
    """Authenticate using MetaMask signature"""
    if not verify_metamask_signature(
        request.wallet_address,
        request.signature,
        request.message
    ):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Store login in database
    login = TLogin(
        wallet_address=request.wallet_address.lower(),
        login_time=datetime.now(timezone.utc)
    )
    await login.insert()
    
    # Generate JWT token
    token = create_jwt_token(request.wallet_address)
    return {"token": token}

@router.post("/auth/manual-login")
async def manual_login(request: ManualLoginRequest):
    """Manual login for testing (bypasses MetaMask)"""
    # Generate JWT token
    token = create_jwt_token(request.wallet_address)
    return {"token": token}

@router.get("/auth/verify")
async def verify_token(authorization: str = Depends(security)):
    """Verify JWT token validity"""
    token = authorization.credentials
    payload = verify_jwt_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"valid": True, "wallet": payload["wallet"]}