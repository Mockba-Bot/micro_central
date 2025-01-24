from fastapi import APIRouter, HTTPException
from typing import Any
from pydantic import BaseModel
from app.utils.getHistorical import get_all_binance, get_historical_data

router = APIRouter()

class BinanceRequest(BaseModel):
    symbol: str
    kline_size: str
    token: str
    save: bool = False

class HistoricalDataRequest(BaseModel):
    pair: str  # Trading pair, e.g., "BTCUSDT"
    timeframe: str  # Time interval, e.g., "1h"
    values: str  # Date range, e.g., "start_date|end_date"    

@router.post("/historical-data")
def fetch_historical_data(request: BinanceRequest):
    """
    Fetch historical data for a Binance symbol.

    Parameters:
        - symbol: The trading pair symbol (e.g., "BTCUSDT").
        - kline_size: Time interval for klines (e.g., "1h").
        - token: User authentication token.
        - save: Whether to save data to the database.

    Returns:
        - Success message or error message.
    """
    try:
        data_df = get_all_binance(
            symbol=request.symbol,
            kline_size=request.kline_size,
            token=request.token,
            save=request.save,
        )
        if data_df is not None:
            return {"message": "Data fetched successfully"}
        else:
            return {"message": "Data updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.post("/query-historical-data")
def query_historical_data(request: HistoricalDataRequest) -> Any:
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
            pair=request.pair,
            timeframe=request.timeframe,
            values=request.values,
        )

        # If data exists, return it as JSON
        if result is not None and not result.empty:
            return result.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries

        # If no data is found
        return {"message": "No data found for the given query."}

    except Exception as e:
        # Handle exceptions and return an HTTP 500 response
        raise HTTPException(status_code=500, detail=f"Error querying data: {str(e)}")