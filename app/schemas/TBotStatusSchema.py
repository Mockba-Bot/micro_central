from pydantic import BaseModel
from datetime import datetime

class TBotStatusSchema(BaseModel):
    status: int
    token: int
    pair: str
    timeframe: str
    creation_date: datetime

    class Config:
        orm_mode = True  # This allows the conversion from SQLAlchemy models to Pydantic models
