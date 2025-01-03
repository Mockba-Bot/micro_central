from sqlalchemy import Column, Integer, String
from app.database import Base

class BinanceCoingeckoMapping(Base):
    __tablename__ = 'binance_coingecko_mapping'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    binance_symbol = Column(String, nullable=False)
    coingecko_id = Column(String, nullable=False)

    def __repr__(self):
        return f'<BinanceCoingeckoMapping {self.id} {self.binance_symbol} {self.coingecko_id}>'