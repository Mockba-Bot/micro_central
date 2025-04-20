# IMPORTS
import sys
import os
import pandas as pd
import os.path
import redis
import pickle
from dotenv import load_dotenv
# # Import custom operations module for database connection
# Add the project root to sys.path
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.utils import operations
from sqlalchemy.sql import text

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")
# Initialize Redis connection
try:
    redis_client = redis.from_url(os.getenv("REDIS_URL"))
    redis_client.ping()
except redis.ConnectionError as e:
    print(f"Redis connection error: {e}")
    redis_client = None

def get_user_data(api_telegram: int) -> pd.DataFrame:
    # Check if data is in Redis cache
    cached_data = redis_client.get(f"user_data:{api_telegram}")
    if cached_data:
        # print("Using cached data")
        return pickle.loads(cached_data)

    # If not in cache, call the operations.getUser function
    df = operations.getUser(api_telegram)
    if df is None:
        raise ValueError("User not found")

    # Store the DataFrame in Redis cache
    redis_client.set(f"user_data:{api_telegram}", pickle.dumps(df))

    return df

# Fetch historical data from the database
def get_historical_data(pair, timeframe, values):
    field = '"start_timestamp"'
    table = f'"{pair}_{timeframe}"'
    start_date, end_date = values.split('|')
    
    query = text(f"""
    SELECT start_timestamp, low, high, volume, open, close
    FROM public.{table}
    WHERE start_timestamp >= :start_time AND start_timestamp <= :end_time
    ORDER BY 1
    """)
    
    # Use parameterized query to avoid SQL injection
    df = pd.read_sql(query, con=operations.db_con_historical, params={"start_time": start_date, "end_time": end_date})
    
    # Convert columns to numeric types
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['volume'] = pd.to_numeric(df['volume'])
    
    return df


# Fetch historical data for trading
# pair = "PERP_APT_USDT"
# timeframe = "1h"
# values = "2025-01-01|2025-01-31"
# result = get_historical_data(pair, timeframe, values)
# print(result.head())
