from sqlalchemy import Column, String, Numeric, Date
from app.database import Base

class TVolumeRecord(Base):
    __tablename__ = "t_volume_records"

    date = Column(Date, primary_key=True)
    account_id = Column(String(66), primary_key=True)
    perp_volume = Column(Numeric(20, 8))
    perp_taker_volume = Column(Numeric(20, 8))
    perp_maker_volume = Column(Numeric(20, 8))
    total_fee = Column(Numeric(20, 8))
    broker_fee = Column(Numeric(20, 8))
    address = Column(String(42))
    broker_id = Column(String(50))
    realized_pnl = Column(Numeric(20, 8))