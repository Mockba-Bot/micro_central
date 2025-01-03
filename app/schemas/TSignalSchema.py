from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Signal schema
class TSignalSchema(BaseModel):
    id: Optional[int]  # We make 'id' optional here because it will be auto-generated
    signal: int
    token: int
    pair: str
    timeframe: str
    gain_threshold: float = 0.001
    stop_loss_threshold: Optional[float] = None
    creation_date: datetime

    class Config:
        orm_mode = True  # This allows the conversion from SQLAlchemy models to Pydantic models
