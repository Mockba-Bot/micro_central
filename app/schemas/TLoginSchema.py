from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TLoginBase(BaseModel):
    token: int
    name: Optional[str]
    last_name: Optional[str]
    is_owner: bool = False
    want_signal: bool = True
    creation_date: datetime
    language: str = 'es'

class TLoginCreate(TLoginBase):
    pass

class TLogin(TLoginBase):
    id: int

    class Config:
        orm_mode = True
