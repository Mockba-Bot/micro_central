from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class TrainingInProgress(Base):
    __tablename__ = 'training_in_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    model_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)

    def __repr__(self):
        return f'<TrainingInProgress {self.id} {self.model_name} {self.status}>'
