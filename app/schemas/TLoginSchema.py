from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class TLoginBase(BaseModel):
    token: int
    api_key: Optional[str]
    api_secret: Optional[str]
    name: Optional[str]
    last_name: Optional[str]
    is_owner: bool = False
    want_signal: bool = True
    wallets: Optional[dict]
    creation_date: datetime
    end_subscription: date

class TLoginCreate(TLoginBase):
    pass

class TLogin(TLoginBase):
    id: int

    class Config:
        orm_mode = True
