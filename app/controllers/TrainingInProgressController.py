from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TrainingInProgress
from app.schemas import TrainingInProgressSchema
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

# Create a new TrainingInProgress
@router.post("/training_in_progress", response_model=TrainingInProgressSchema)
async def create_training_in_progress(training: TrainingInProgressSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_training = TrainingInProgress(pair_timeframe=training.pair_timeframe)
        db.add(new_training)
        await db.commit()
        await db.refresh(new_training)
        return new_training
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Retrieve a TrainingInProgress by ID
@router.get("/training_in_progress/{id}", response_model=TrainingInProgressSchema)
async def get_training_in_progress(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TrainingInProgress).filter(TrainingInProgress.id == id))
        training = result.scalars().first()
        if not training:
            raise HTTPException(status_code=404, detail="TrainingInProgress not found")
        return training
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update a TrainingInProgress by ID
@router.put("/training_in_progress/{id}", response_model=TrainingInProgressSchema)
async def update_training_in_progress(id: int, training: TrainingInProgressSchema, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TrainingInProgress).filter(TrainingInProgress.id == id))
        existing_training = result.scalars().first()
        if not existing_training:
            raise HTTPException(status_code=404, detail="TrainingInProgress not found")

        # Update fields
        existing_training.pair_timeframe = training.pair_timeframe

        await db.commit()
        await db.refresh(existing_training)
        return existing_training
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete a TrainingInProgress by ID
@router.delete("/training_in_progress/{id}")
async def delete_training_in_progress(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TrainingInProgress).filter(TrainingInProgress.id == id))
        existing_training = result.scalars().first()
        if not existing_training:
            raise HTTPException(status_code=404, detail="TrainingInProgress not found")

        await db.delete(existing_training)
        await db.commit()
        return {"message": "TrainingInProgress deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
