from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TLoginBase(BaseModel):
    token: int
    wallet_address: Optional[str]
    want_signal: bool = True
    language: str = 'en'

class TLoginCreate(TLoginBase):
    pass

class TLogin(TLoginBase):
    id: int

    class Config:
        orm_mode = True

class LoginRequest(BaseModel):
    """Request model for MetaMask login"""
    wallet_address: str
    signature: str
    message: str

class ManualLoginRequest(BaseModel):
    """Request model for manual login (testing)"""
    wallet_address: str
