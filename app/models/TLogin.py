from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from datetime import datetime, timezone
from app.database import Base

class TLogin(Base):
    __tablename__ = 't_login'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(BigInteger, nullable=False)
    wallet_address = Column(String, unique=True)  # Make wallet_address unique
    want_signal = Column(Boolean, default=True)
    creation_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    language = Column(String, default='es')

    def __repr__(self):
        return f'<TLogin {self.token}>'
