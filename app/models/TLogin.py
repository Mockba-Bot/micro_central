from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from datetime import datetime
from app.database import Base

class TLogin(Base):
    __tablename__ = 't_login'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(BigInteger, nullable=False, unique=True)
    name = Column(String)
    last_name = Column(String)
    is_owner = Column(Boolean, default=False, nullable=False)
    want_signal = Column(Boolean, default=True)
    creation_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    language = Column(String, default='es')

    def __repr__(self):
        return f'<TLogin {self.token}>'
