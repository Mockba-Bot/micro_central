import os
from dotenv import load_dotenv
import psycopg2
import schedule
import time
import sys

# Access the environment variables
PATH_OPERATIONS = os.getenv("PATH_OPERATIONS")
sys.path.append(PATH_OPERATIONS)
from database import operations

# Import the logger
PATH_LOGS = os.getenv("PATH_LOGS")
sys.path.append(PATH_LOGS)
from log_config import trader_logger, gainers_logger  # Import the two loggers

# loading the .env file
# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# access the environment variables
host = os.getenv("HOST")
database = os.getenv("DATABASE")
user = os.getenv("USR")
password = os.getenv("PASSWD")

# def verifyUser():
#     try:
#         conn = psycopg2.connect(host=host, database=database, user=user, password=password)
#         cursor = conn.cursor()
#         # insert data into the database
#         sql = f"select * from public.delete_user()"
#         cursor.execute(sql)
#         gcount = cursor.rowcount
#         if gcount == 0:
#             print("No user to delete")
#         # commit the transaction
#         conn.commit()
#     except psycopg2.Error as e:
#         gcount = 0
#         print("Error:", e)
#     finally:
#         # close the cursor and connection
#         cursor.close()
#         if conn is not None:
#            conn.close() 

def job():
    verifyUser()

def start():
    print("Cron Job started...")
    trader_logger.info("Cron Job started, checking users...")
    schedule.every(2).hours.do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)    

# if __name__ == "__main__":
#     print("Cron Job started...")
#     schedule.every(2).hours.do(job)

#     while True:
#         schedule.run_pending()
#         time.sleep(1)
              