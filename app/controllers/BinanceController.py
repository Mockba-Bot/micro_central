from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.getHistorical import get_all_binance

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