from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import TBotStatus
from app.schemas import TBotStatusSchema
from app.database import get_db
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

# Create a new TBotStatus
@router.post("/t_bot_status", response_model=TBotStatusSchema)
async def create_t_bot_status(status: TBotStatusSchema, db: AsyncSession = Depends(get_db)):
    try:
        new_status = TBotStatus(
            status=status.status,
            token=status.token,
            pair=status.pair,
            timeframe=status.timeframe
        )
        db.add(new_status)
        await db.commit()
        await db.refresh(new_status)
        return new_status
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Retrieve a TBotStatus by token, pair, and timeframe
@router.get("/t_bot_status/{token}/{pair}/{timeframe}", response_model=TBotStatusSchema)
async def get_t_bot_status(token: int, pair: str, timeframe: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TBotStatus).filter(
            TBotStatus.token == token,
            TBotStatus.pair == pair,
            TBotStatus.timeframe == timeframe
        ))
        status = result.scalars().first()
        if not status:
            raise HTTPException(status_code=404, detail="TBotStatus not found")
        return status
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Update an existing TBotStatus by token, pair, and timeframe
@router.put("/t_bot_status/{token}/{pair}/{timeframe}", response_model=TBotStatusSchema)
async def update_t_bot_status(token: int, pair: str, timeframe: str, status: TBotStatusSchema, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TBotStatus).filter(
            TBotStatus.token == token,
            TBotStatus.pair == pair,
            TBotStatus.timeframe == timeframe
        ))
        existing_status = result.scalars().first()
        if not existing_status:
            raise HTTPException(status_code=404, detail="TBotStatus not found")

        # Update fields
        existing_status.status = status.status
        existing_status.creation_date = status.creation_date

        await db.commit()
        await db.refresh(existing_status)
        return existing_status
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete a TBotStatus by token, pair, and timeframe
@router.delete("/t_bot_status/{token}/{pair}/{timeframe}")
async def delete_t_bot_status(token: int, pair: str, timeframe: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TBotStatus).filter(
            TBotStatus.token == token,
            TBotStatus.pair == pair,
            TBotStatus.timeframe == timeframe
        ))
        existing_status = result.scalars().first()
        if not existing_status:
            raise HTTPException(status_code=404, detail="TBotStatus not found")

        await db.delete(existing_status)
        await db.commit()
        return {"message": "TBotStatus deleted successfully"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
