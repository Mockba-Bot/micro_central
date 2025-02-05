# IMPORTS
import sys
import os
import os.path
import time
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import logging
from sqlalchemy import create_engine
import psycopg2

from app.utils import operations, security
from sqlalchemy.sql import text

# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# Assuming operations.db_con is a SQLAlchemy engine
def get_capital_accumulated(token, pair, timeframe):
    try:
        query = """
            SELECT capital_accumulated FROM capital
            WHERE token = %s AND pair = %s AND timeframe = %s
            ORDER BY timestamp DESC LIMIT 1;
        """
        # Use parameterized query to avoid SQL injection
        result = pd.read_sql(query, con=operations.db_con, params=[token, pair, timeframe])
        if not result.empty:
            return float(result.iloc[0]['capital_accumulated'])
        else:
            return None
    except Exception as e:
        trader_logger.error(f"Error retrieving capital_accumulated for token {token}, pair {pair}, and timeframe {timeframe}: {e}")
        return None

# Update the capital_accumulated field in the database
def update_capital_accumulated(token, pair, timeframe, capital_accumulated):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(host=operations.host, database=operations.database, user=operations.user, password=operations.password)
        cursor = conn.cursor()
        query = """
            UPDATE capital
            SET capital_accumulated = %s
            WHERE token = %s AND pair = %s AND timeframe = %s;
        """
        # Use parameterized query to avoid SQL injection
        cursor.execute(query, (capital_accumulated, token, pair, timeframe))
        conn.commit()
        trader_logger.info(f"Capital accumulated updated for token {token}, pair {pair}, and timeframe {timeframe}")
    except Exception as e:
        trader_logger.error(f"Error updating capital_accumulated: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Store capital and crypto amount in the database
def store_capital(token, pair, timeframe, capital, crypto_amount, timestamp, cumulative_strategy_return, cumulative_market_return, first_trade, last_price=0.0):
    if capital < 0:
        capital = 0
    
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(host=operations.host, database=operations.database, user=operations.user, password=operations.password)
        cursor = conn.cursor()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        query = """
            INSERT INTO capital(token, pair, timeframe, capital, crypto_amount, timestamp, cumulative_strategy_return, cumulative_market_return, first_trade, last_price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (token, pair, timeframe) DO UPDATE
            SET capital = EXCLUDED.capital, crypto_amount = EXCLUDED.crypto_amount, timestamp = EXCLUDED.timestamp,
                cumulative_strategy_return = EXCLUDED.cumulative_strategy_return, cumulative_market_return = EXCLUDED.cumulative_market_return, first_trade = EXCLUDED.first_trade, last_price = EXCLUDED.last_price;
        """
        # Use parameterized query to avoid SQL injection
        cursor.execute(query, (token, pair, timeframe, capital, crypto_amount, timestamp, cumulative_strategy_return, cumulative_market_return, first_trade, last_price))
        conn.commit()
        trader_logger.info(f"Capital and crypto amount stored for token {token}, pair {pair}, and timeframe {timeframe}")
    except Exception as e:
        trader_logger.error(f"Error storing capital and crypto amount: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Update the capital in the database
def updateCapitalTimestamp(token, pair, timeframe, timestamp):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(host=operations.host, database=operations.database, user=operations.user, password=operations.password)
        cursor = conn.cursor()
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        query = """
            UPDATE capital
            SET timestamp = %s
            WHERE token = %s AND pair = %s AND timeframe = %s;
        """
        # Use parameterized query to avoid SQL injection
        cursor.execute(query, (timestamp, token, pair, timeframe))
        conn.commit()
        trader_logger.info(f"Timestamp updated for token {token}, pair {pair}, and timeframe {timeframe} at {timestamp}")
    except Exception as e:
        trader_logger.error(f"Error updating timestamp: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Update the crypto amount in the database
def updateCapitalCrypto(token, pair, timeframe, crypto_amount):
    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(host=operations.host, database=operations.database, user=operations.user, password=operations.password)
        cursor = conn.cursor()
        query = """
            UPDATE capital
            SET crypto_amount = %s
            WHERE token = %s AND pair = %s AND timeframe = %s;
        """
        # Use parameterized query to avoid SQL injection
        cursor.execute(query, (crypto_amount, token, pair, timeframe))
        conn.commit()
        trader_logger.info(f"Crypto amount updated for token {token}, pair {pair}, and timeframe {timeframe}")
    except Exception as e:
        trader_logger.error(f"Error updating crypto amount: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# get capital from the database
def get_capital(token, pair, timeframe):
    try:
        query = """
            SELECT capital, crypto_amount, timestamp, cumulative_strategy_return, cumulative_market_return, first_trade, last_price FROM capital
            WHERE token = %s AND pair = %s AND timeframe = %s
            ORDER BY timestamp DESC LIMIT 1;
        """
        # Use parameterized query to avoid SQL injection
        result = pd.read_sql(query, con=operations.db_con, params=[token, pair, timeframe])
        if not result.empty:
            return (
                float(result.iloc[0]['capital']),
                float(result.iloc[0]['crypto_amount']),
                pd.to_datetime(result.iloc[0]['timestamp']),
                float(result.iloc[0]['cumulative_strategy_return']),
                float(result.iloc[0]['cumulative_market_return']),
                result.iloc[0]['first_trade'],
                float(result.iloc[0]['last_price'])
            )
        else:
            return None, None, None, None, None, None, None
    except Exception as e:
        trader_logger.error(f"Error retrieving capital for token {token}, pair {pair}, and timeframe {timeframe}: {e}")
        return None, None, None, None, None, None, None