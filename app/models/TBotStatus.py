from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import Base

class TBotStatus(Base):
    __tablename__ = 't_bot_status'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<TBotStatus {self.id} {self.status} {self.last_updated}>'
