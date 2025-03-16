import os
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

# loading the .env file
# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
database_historical = os.getenv("DATABASE_HISTORICAL")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# # Print environment variables for debugging
# print(f"HOST: {host}")
# print(f"DATABASE: {database}")
# print(f"USR: {user}")
# print(f"PASSWD: {password}")

# # Check if environment variables are loaded correctly
# if not all([host, database, user, password]):
#     raise ValueError("One or more environment variables are missing")

db_con = create_engine(f"postgresql://{user}:{password}@{host}:5432/{database}")   
db_con_historical = create_engine(f"postgresql://{user}:{password}@{host}:5432/{database_historical}")
df = ""

def getUser(token):
    try:
        # Get a connection from the engine
        with db_con.connect() as conn:
            # Use the connection to query the database
            df = pd.read_sql(f"SELECT * FROM t_login WHERE token = {token}", con=conn)
            if df.empty:
                return None
            return df
    except Exception as e:
        print(f"Error: {e}")
        return None

# Def get signal
def getSignal(token, pair, timeframe):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Select data from the t_signal table
        sql = f"SELECT * FROM t_signal WHERE token = {token} AND pair = '{pair}' AND timeframe = '{timeframe}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.commit()
        if result is None:
            return None
    except psycopg2.Error as e:
        print("Error:", e)
        return None
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()
            
# Def trendTime
def addTsignal(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "insert into t_signal (signal,token,pair,timeframe,gain_threshold,stop_loss_threshold) values (%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 

# Def trendTime
def resetTokenSignal(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "delete from t_signal where token=%s and pair=%s and timeframe=%s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()                       

# Def trendTime
def resetToken(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "delete from capital where token=%s and pair=%s and timeframe=%s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()
    

# Def trendTime
def startStopBotOp(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "update t_signal set signal = %s where token = %s and pair = %s and timeframe = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 


# Def startStop Signals
def startStopSignalOp(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "update t_login set want_signal = %s where token = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close() 


def startStopBotAutoGainers(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "update capital_trader_gainers set signal = %s where token = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()

def getCapitalGainers(token):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Select data from the t_signal table
        sql =  query = f"""
            SELECT capital FROM capital_trader_gainers
            WHERE token = '{token}';
        """
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.commit()
        if result is None:
            return None
        else:
            return result[0]    
    except psycopg2.Error as e:
        print("Error:", e)
        return None
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

def store_capital_gainer(token, capital):  
    data = (token, capital)  
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"""
            INSERT INTO capital_trader_gainers(token, capital)
            VALUES (%s, %s)
            ON CONFLICT (token) DO UPDATE
            SET capital = EXCLUDED.capital, 
        """
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

# Def trendTime
def updateThreshold(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = "update t_signal set gain_threshold = %s, stop_loss_threshold = %s where token = %s and pair = %s and timeframe = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
           conn.close()                
         
# Set dynamic model path based on pair and timeframe
def get_model_path(pair, timeframe):
    return f'trained_models/trained_model_{pair}_{timeframe}.pkl' 

# Def addTraining
def addTraining(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Ensure data is a tuple with a single element
        if not isinstance(data, tuple):
            data = (data,)
        # Insert data into the database
        sql = "INSERT INTO training_in_progress (pair_timeframe) VALUES (%s)"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # Commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()
    return gcount

# Def deleteTraining
def deleteTraining(data):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Ensure data is a tuple with a single element
        if not isinstance(data, tuple):
            data = (data,)
        # Delete data from the database
        sql = "DELETE FROM training_in_progress WHERE pair_timeframe = %s"
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # Commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()
    return gcount


# Def deleteTraining
async def remove_null_timestamps(table_name):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Ensure data is a tuple with a single element
        # if not isinstance(data, tuple):
        #     data = (data,)
        # Delete data from the database
        sql = f'DELETE FROM public."{table_name}" WHERE "timestamp" IS NULL;'
        cursor.execute(sql)
        # Commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

# Def get signal
def getTraining(timeframe):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Select data from the t_signal table
        sql = f"SELECT * FROM training_in_progress WHERE pair_timeframe = '{timeframe}'"
        cursor.execute(sql)
        result = cursor.fetchone()
        conn.commit()
        if result is None:
            return None
        else:
            return result    
    except psycopg2.Error as e:
        print("Error:", e)
        return None
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

# Drop duplicates from SQL table Historical
def remove_null_from_sql_table(table_name):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # Delete rows with null timestamp from the specified table
        sql = f"""
        DELETE FROM public."{table_name}"
        WHERE timestamp is null;
        """
        cursor.execute(sql)
        conn.commit()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_capital_info(token):
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()

        # Execute the SQL query to filter by token
        query = """
        SELECT pair, timeframe, capital, crypto_amount
        FROM public.capital
        WHERE token = %s
        """
        cursor.execute(query, (token,))

        # Fetch all results
        results = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        if results:
            # Format the crypto_amount to 4 decimal places for each row
            formatted_results = [
                (pair, timeframe, capital, round(float(crypto_amount), 4))
                for pair, timeframe, capital, crypto_amount in results
            ]
            return formatted_results
        else:
            return None  # No matching token found

    except Exception as e:
        print(f"Error: {e}")
        return None 

# Store New Users or Owner
def store_user(token, api_key, api_secret, name, last_name, is_owner = False):  
    data = (token, api_key, api_secret, name, last_name, is_owner)  
    try:
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()
        # insert data into the database
        sql = f"""
            INSERT INTO t_login(token, api_key, api_secret, name, last_name, is_owner)
            VALUES (%s, %s, %s,%s, %s, %s)
            ON CONFLICT (token) DO UPDATE
            SET api_key = EXCLUDED.api_key, 
                api_secret = EXCLUDED.api_secret,
                name = EXCLUDED.name,
                last_name = EXCLUDED.last_name
                ;
        """
        cursor.execute(sql, data)
        gcount = cursor.rowcount
        # commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

# Validate OwnerShip if the user is owner or not
def validatOwner(token):
    df = pd.read_sql(f"SELECT * FROM  t_login where token = {token} and is_owner = True" ,con=db_con)
    if df.empty:
        return None
    return df


# Delete user
def del_user(token):
    try:
        with psycopg2.connect(host=host, database=database, user=user, password=password) as conn:
            with conn.cursor() as cursor:
                # Delete data from the database
                sql_statements = [
                    "DELETE FROM t_signal WHERE token = %s;",
                    "DELETE FROM capital WHERE token = %s;",
                    "DELETE FROM capital_trader_gainers WHERE token = %s ;",
                    "DELETE FROM t_bot_status WHERE token = %s;",
                    "DELETE FROM trader_gainers WHERE token = %s;",
                    "DELETE FROM t_login WHERE token = %s and is_owner = False;"
                ]
                
                for sql in sql_statements:
                    cursor.execute(sql, (token,))
                
                # Commit the transaction
                conn.commit()
                
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)

# Def scalper
def add_scalper(data):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(host=host, database=database, user=user, password=password)
        cursor = conn.cursor()

        # SQL insert statement
        sql = """
        INSERT INTO scalper (
            token, pair, timeframe, capital, crypto_amount, crypto_remaining, timestamp, rowcount, position, 
            last_partial_exit_price, partial_exit_done, signal, first_trade, entry_price, 
            stop_loss_percentage, profit_target_from, profit_target_to, 
            partial_exit_threshold_from, partial_exit_threshold_to, 
            exit_remaining_percentage_from, exit_remaining_percentage_to, 
            partial_exit_amount
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Execute the insert statement
        cursor.execute(sql, data)
        gcount = cursor.rowcount

        # Commit the transaction
        conn.commit()
    except psycopg2.Error as e:
        gcount = 0
        print("Error:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        if conn is not None:
            conn.close()

    return gcount

# data = (
#     556159355,                # token
#     "SOLUSDT",                # pair
#     "5m",                     # timeframe
#     100.0,                    # capital
#     0.0,                      # crypto_amount
#     0.0,                      # crypto_remaining
#     "2024-10-28 10:00:00",    # timestamp (in 'YYYY-MM-DD HH:MM:SS' format)
#     0,                        # rowcount
#     0,                        # position
#     0.0,                      # last_partial_exit_price
#     False,                    # partial_exit_done
#     1,                        # signal
#     True,                     # first_trade
#     0,                        # entry_price
#     0.15,                     # stop_loss_percentage
#     0.3,                      # profit_target_from
#     3.0,                      # profit_target_to
#     20.0,                     # partial_exit_threshold_from
#     25.0,                     # partial_exit_threshold_to
#     20.0,                     # exit_remaining_percentage_from
#     25.0,                     # exit_remaining_percentage_to
#     0.30                      # partial_exit_amount
# )

# rows_inserted = add_scalper(data)
# print(f"Rows inserted: {rows_inserted}")    
