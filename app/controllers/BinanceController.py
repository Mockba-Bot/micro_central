from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.getHistorical import get_all_binance, get_historical_data

router = APIRouter()

class BinanceRequest(BaseModel):
    symbol: str
    kline_size: str
    token: str
    save: bool = False

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
            return {"message": "No data found."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


@router.post("/query-historical-data")
def query_historical_data(request: HistoricalDataRequest):
    """
    Query historical data from the database for a trading pair.

    Parameters:
        - pair: The trading pair symbol (e.g., "BTCUSDT").
        - timeframe: Time interval for klines (e.g., "1h").
        - values: Date range for data, in the format "start_date|end_date" (e.g., "2024-01-01|2024-01-31").

    Returns:
        - DataFrame as a JSON object.
    """
    try:
        data_df = get_historical_data(
            pair=request.pair,
            timeframe=request.timeframe,
            values=request.values,
        )
        if not data_df.empty:
            return data_df.to_dict(orient="records")
        else:
            return {"message": "No data found for the given query."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying data: {str(e)}")
