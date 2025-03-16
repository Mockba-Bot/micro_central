from fastapi import APIRouter, HTTPException, Query, Request
from typing import Any
from pydantic import BaseModel
from app.utils.capital import (
    get_capital_accumulated,
    update_capital_accumulated,
    store_capital,
    updateCapitalTimestamp,
    updateCapitalCrypto,
    get_capital,
    get_trader_info
)
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

class CapitalAccumulatedRequest(BaseModel):
    token: str
    pair: str
    timeframe: str

class UpdateCapitalAccumulatedRequest(BaseModel):
    token: str
    pair: str
    timeframe: str
    capital_accumulated: float

class StoreCapitalRequest(BaseModel):
    token: str
    pair: str
    timeframe: str
    capital: float
    crypto_amount: float
    timestamp: str
    cumulative_strategy_return: float
    cumulative_market_return: float
    first_trade: bool
    last_price: float = 0.0

class UpdateCapitalTimestampRequest(BaseModel):
    token: str
    pair: str
    timeframe: str
    timestamp: str

class UpdateCapitalCryptoRequest(BaseModel):
    token: str
    pair: str
    timeframe: str
    crypto_amount: float

class GetCapitalRequest(BaseModel):
    token: str
    pair: str
    timeframe: str

@router.get("/capital/accumulated")
def get_capital_accumulated_route(request: CapitalAccumulatedRequest):
    """
    Fetch the accumulated capital for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.

    Returns:
        - A JSON object with the accumulated capital.
    """
    try:
        result = get_capital_accumulated(request.token, request.pair, request.timeframe)
        return {"capital_accumulated": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving capital accumulated: {str(e)}")

@router.put("/capital/accumulated")
def update_capital_accumulated_route(request: UpdateCapitalAccumulatedRequest):
    """
    Update the accumulated capital for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.
        - capital_accumulated: The new accumulated capital value.

    Returns:
        - A success message.
    """
    try:
        update_capital_accumulated(request.token, request.pair, request.timeframe, request.capital_accumulated)
        return {"message": "Capital accumulated updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating capital accumulated: {str(e)}")

@router.post("/capital")
def store_capital_route(request: StoreCapitalRequest):
    """
    Store capital and related data for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.
        - capital: The capital value.
        - crypto_amount: The amount of cryptocurrency.
        - timestamp: The timestamp of the data.
        - cumulative_strategy_return: The cumulative strategy return.
        - cumulative_market_return: The cumulative market return.
        - first_trade: Whether it is the first trade.
        - last_price: The last price (optional).

    Returns:
        - A success message.
    """
    try:
        store_capital(
            request.token,
            request.pair,
            request.timeframe,
            request.capital,
            request.crypto_amount,
            datetime.strptime(request.timestamp, '%Y-%m-%d %H:%M:%S'),
            request.cumulative_strategy_return,
            request.cumulative_market_return,
            request.first_trade,
            request.last_price
        )
        return {"message": "Capital stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing capital: {str(e)}")

@router.put("/capital/timestamp")
def update_capital_timestamp_route(request: UpdateCapitalTimestampRequest):
    """
    Update the timestamp for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.
        - timestamp: The new timestamp.

    Returns:
        - A success message.
    """
    try:
        updateCapitalTimestamp(
            request.token,
            request.pair,
            request.timeframe,
            datetime.strptime(request.timestamp, '%Y-%m-%d %H:%M:%S')
        )
        return {"message": "Timestamp updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating timestamp: {str(e)}")

@router.put("/capital/crypto")
def update_capital_crypto_route(request: UpdateCapitalCryptoRequest):
    """
    Update the crypto amount for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.
        - crypto_amount: The new crypto amount.

    Returns:
        - A success message.
    """
    try:
        updateCapitalCrypto(
            request.token,
            request.pair,
            request.timeframe,
            request.crypto_amount
        )
        return {"message": "Crypto amount updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating crypto amount: {str(e)}")

@router.get("/capital")
def get_capital_route(request: GetCapitalRequest):
    """
    Fetch the capital data for a given token, pair, and timeframe.

    Parameters:
        - token: The token identifier.
        - pair: The trading pair.
        - timeframe: The timeframe for the capital data.

    Returns:
        - A JSON object with the capital data.
    """
    try:
        capital, crypto_amount, timestamp, cumulative_strategy_return, cumulative_market_return, first_trade, last_price = get_capital(request.token, request.pair, request.timeframe)
        return {
            "capital": capital,
            "crypto_amount": crypto_amount,
            "timestamp": timestamp,
            "cumulative_strategy_return": cumulative_strategy_return,
            "cumulative_market_return": cumulative_market_return,
            "first_trade": first_trade,
            "last_price": last_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving capital: {str(e)}")

@router.get("/trader-info")
def get_trader_info_route(page: int = Query(1, ge=1), page_size: int = Query(1000, ge=1)):
    """
    Fetch information about the trader in paginated chunks.

    Parameters:
        - page: The page number (default is 1).
        - page_size: The number of items per page (default is 1000).

    Returns:
        - A JSON object with the trader information.
    """
    try:
        result = get_trader_info(page, page_size)
        return result.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving trader information: {str(e)}")
