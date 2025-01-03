from pydantic import BaseModel
from typing import Optional

class TrainingInProgressSchema(BaseModel):
    id: Optional[int]  # 'id' is optional for the request, as it's auto-generated
    pair_timeframe: str

    class Config:
        orm_mode = True  # This allows the conversion from SQLAlchemy models to Pydantic models
