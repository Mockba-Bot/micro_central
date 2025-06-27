from pydantic import BaseModel
from datetime import date
from typing import Optional

class TVolumeRecordBase(BaseModel):
    date: date
    account_id: str
    perp_volume: float
    perp_taker_volume: float
    perp_maker_volume: float
    total_fee: float
    broker_fee: float
    address: str
    broker_id: str
    realized_pnl: float

class TVolumeRecordCreate(TVolumeRecordBase):
    pass

class TVolumeRecord(TVolumeRecordBase):
    class Config:
        orm_mode = True