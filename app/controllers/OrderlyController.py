from fastapi import APIRouter, HTTPException
from typing import Any
from pydantic import BaseModel
from app.utils.getHistorical import get_historical_data

router = APIRouter()

class HistoricalDataRequest(BaseModel):
    pair: str  # Trading pair, e.g., "BTCUSDT"
    timeframe: str  # Time interval, e.g., "1h"
    values: str  # Date range, e.g., "start_date|end_date"    


@router.post("/query-historical-data")
async def query_historical_data(historical_data_request: HistoricalDataRequest) -> Any:
    """
    Query historical data from the database for a trading pair.

    Parameters:
        - request: HistoricalDataRequest object containing query parameters.

    Returns:
        - A JSON object with the historical data or a message if no data is found.
    """
    try:
        # Call the function to fetch data
        result = get_historical_data(
            pair=historical_data_request.pair,
            timeframe=historical_data_request.timeframe,
            values=historical_data_request.values,
        )
        # If data exists, return it as JSON
        if result is not None and not result.empty:
            return result.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries

        # If no data is found
        return {"message": "No data found for the given query."}

    except Exception as e:
        # Handle exceptions and return an HTTP 500 response
        raise HTTPException(status_code=500, detail=f"Error querying data: {str(e)}")