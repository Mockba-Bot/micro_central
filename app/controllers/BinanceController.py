from fastapi import APIRouter, HTTPException, Request
from typing import Any
from pydantic import BaseModel
from app.utils.getHistorical import get_all_binance, get_historical_data, get_historical_data_for_trade
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

router = APIRouter()

# Initialize the rate limiter
limiter = Limiter(key_func=get_remote_address)

class BinanceRequest(BaseModel):
    symbol: str
    kline_size: str
    token: str
    save: bool = False

class HistoricalDataRequest(BaseModel):
    pair: str  # Trading pair, e.g., "BTCUSDT"
    timeframe: str  # Time interval, e.g., "1h"
    values: str  # Date range, e.g., "start_date|end_date"    

class HistoricalDataForTradeRequest(BaseModel):
    pair: str  # Trading pair, e.g., "BTCUSDT"
    timeframe: str  # Time interval, e.g., "1h"
    limit: int  # Number of records to fetch    

@router.post("/historical-data")
@limiter.limit("10/second")
async def fetch_historical_data(request: Request, binance_request: BinanceRequest):
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
            symbol=binance_request.symbol,
            kline_size=binance_request.kline_size,
            token=binance_request.token,
            save=binance_request.save,
        )
        if data_df is not None:
            return {"message": "Data fetched successfully"}
        else:
            return {"message": "Data updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@router.post("/query-historical-data")
@limiter.limit("10/second")
async def query_historical_data(request: Request, historical_data_request: HistoricalDataRequest) -> Any:
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

@router.post("/query-historical-data-for-trade")
@limiter.limit("10/second")
async def query_historical_data_for_trade(request: Request, historical_data_for_trade_request: HistoricalDataForTradeRequest) -> Any:
    """
    Query historical data from the database for a trading pair.

    Parameters:
        - request: HistoricalDataRequest object containing query parameters.

    Returns:
        - A JSON object with the historical data or a message if no data is found.
    """
    try:
        # Call the function to fetch data
        result = get_historical_data_for_trade(
            pair=historical_data_for_trade_request.pair,
            timeframe=historical_data_for_trade_request.timeframe,
            limit=historical_data_for_trade_request.limit,
        )

        # If data exists, return it as JSON
        if result is not None and not result.empty:
            return result.to_dict(orient="records")  # Convert DataFrame to a list of dictionaries

        # If no data is found
        return {"message": "No data found for the given query."}

    except Exception as e:
        # Handle exceptions and return an HTTP 500 response
        raise HTTPException(status_code=500, detail=f"Error querying data: {str(e)}")

# Add exception handler for rate limit exceeded
@router.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."}
    )