from sqlalchemy import Column, Integer, BigInteger, String, Boolean, JSON, DateTime, Date
from datetime import datetime, date
from app.database import Base

class TLogin(Base):
    __tablename__ = 't_login'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(BigInteger, nullable=False, unique=True)
    api_key = Column(String, nullable=False)
    api_secret = Column(String)
    name = Column(String)
    last_name = Column(String)
    is_owner = Column(Boolean, default=False, nullable=False)
    want_signal = Column(Boolean, default=True)
    wallets = Column(JSON)  # Store wallets as JSON
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_subscription = Column(Date, nullable=False, default=date(2080, 12, 31))

    def __repr__(self):
        return f'<TLogin {self.token}>'
