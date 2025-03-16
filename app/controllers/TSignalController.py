from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TSignal
from app.schemas import TSignalSchema
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse

router = APIRouter()

# Create a new TSignal
@router.post("/tsignal", response_model=TSignalSchema)
async def create_tsignal(tsignal: TSignalSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_tsignal = TSignal(
            signal=tsignal.signal,
            token=tsignal.token,
            pair=tsignal.pair,
            timeframe=tsignal.timeframe,
            gain_threshold=tsignal.gain_threshold,
            stop_loss_threshold=tsignal.stop_loss_threshold,
            creation_date=tsignal.creation_date
        )
        db.add(new_tsignal)
        await db.commit()
        await db.refresh(new_tsignal)
        return new_tsignal
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Retrieve a TSignal by ID
@router.get("/tsignal/{id}", response_model=TSignalSchema)
async def get_tsignal(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TSignal).filter(TSignal.id == id))
        tsignal = result.scalars().first()
        if not tsignal:
            raise HTTPException(status_code=404, detail="TSignal not found")
        return tsignal
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update a TSignal by ID
@router.put("/tsignal/{id}", response_model=TSignalSchema)
async def update_tsignal(id: int, tsignal: TSignalSchema, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TSignal).filter(TSignal.id == id))
        existing_tsignal = result.scalars().first()
        if not existing_tsignal:
            raise HTTPException(status_code=404, detail="TSignal not found")

        # Update fields
        existing_tsignal.signal = tsignal.signal
        existing_tsignal.token = tsignal.token
        existing_tsignal.pair = tsignal.pair
        existing_tsignal.timeframe = tsignal.timeframe
        existing_tsignal.gain_threshold = tsignal.gain_threshold
        existing_tsignal.stop_loss_threshold = tsignal.stop_loss_threshold
        existing_tsignal.creation_date = tsignal.creation_date

        await db.commit()
        await db.refresh(existing_tsignal)
        return existing_tsignal
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete a TSignal by ID
@router.delete("/tsignal/{id}")
async def delete_tsignal(id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TSignal).filter(TSignal.id == id))
        existing_tsignal = result.scalars().first()
        if not existing_tsignal:
            raise HTTPException(status_code=404, detail="TSignal not found")

        await db.delete(existing_tsignal)
        await db.commit()
        return {"message": "TSignal deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

