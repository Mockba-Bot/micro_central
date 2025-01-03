from sqlalchemy import Column, Integer, BigInteger, String, Float, DateTime, Index
from datetime import datetime
from app.database import Base

class TSignal(Base):
    __tablename__ = 't_signal'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal = Column(BigInteger, nullable=False)
    token = Column(BigInteger, nullable=False)
    pair = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    gain_threshold = Column(Float, nullable=False, default=0.001)
    stop_loss_threshold = Column(Float)
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx2_token_pair_timeframe', 'token', 'pair', 'timeframe'),
    )

    def __repr__(self):
        return f'<TSignal {self.id} {self.token} {self.pair} {self.timeframe}>'
