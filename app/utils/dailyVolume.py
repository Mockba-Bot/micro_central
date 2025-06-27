import asyncio
import time
import urllib.parse
import requests
from base64 import urlsafe_b64encode
from base58 import b58decode
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import logging
import sys
import os
from dotenv import load_dotenv
import datetime
from collections import defaultdict
from sqlalchemy.dialects.postgresql import insert
from app.database import get_db
from app.models.TVolumeRecord import TVolumeRecord

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# Load environment variables
load_dotenv(dotenv_path=".env.micro.central")

ORDERLY_ACCOUNT_ID = os.getenv("ORDERLY_ACCOUNT_ID")
ORDERLY_SECRET = os.getenv("ORDERLY_SECRET", "").replace("ed25519:", "")
ORDERLY_PUBLIC_KEY = os.getenv("ORDERLY_PUBLIC_KEY")
BASE_URL = os.getenv("ORDERLY_BASE_URL")

# Decode Base58 secret key
private_key = Ed25519PrivateKey.from_private_bytes(b58decode(ORDERLY_SECRET))

# Logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def fetch_broker_daily_volume_orderly():
    timestamp = str(int(time.time() * 1000))
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    params = {
        "start_date": thirty_days_ago.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d")
    }

    path = "/v1/volume/broker/daily"
    query = f"?{urllib.parse.urlencode(params)}"
    message = f"{timestamp}GET{path}{query}"
    signature = urlsafe_b64encode(private_key.sign(message.encode())).decode()

    headers = {
        "orderly-timestamp": timestamp,
        "orderly-account-id": ORDERLY_ACCOUNT_ID,
        "orderly-key": ORDERLY_PUBLIC_KEY,
        "orderly-signature": signature
    }

    url = f"{BASE_URL}{path}{query}"

    try:
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            logger.error(f"Orderly API error: {response.text}")
            return None

        rows = response.json().get("data", {}).get("rows", [])
        if not rows:
            logger.warning("No data rows in response")
            return None

        # Step 1: Group by (date, account_id) and aggregate
        grouped = defaultdict(lambda: {
            "perp_volume": 0,
            "perp_taker_volume": 0,
            "perp_maker_volume": 0,
            "total_fee": 0,
            "broker_fee": 0,
            "realized_pnl": 0,
            "address": "",
            "broker_id": ""
        })

        for row in rows:
            record_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
            key = (record_date, ORDERLY_ACCOUNT_ID)
            grouped[key]["perp_volume"] += row.get("perp_volume", 0) or 0
            grouped[key]["perp_taker_volume"] += row.get("perp_taker_volume", 0) or 0
            grouped[key]["perp_maker_volume"] += row.get("perp_maker_volume", 0) or 0
            grouped[key]["total_fee"] += row.get("total_fee", 0) or 0
            grouped[key]["broker_fee"] += row.get("broker_fee", 0) or 0
            grouped[key]["realized_pnl"] += row.get("realized_pnl", 0) or 0
            grouped[key]["address"] = row.get("address")
            grouped[key]["broker_id"] = row.get("broker_id")

        records = []
        for (record_date, account_id), values in grouped.items():
            records.append({
                "date": record_date,
                "account_id": account_id,
                "perp_volume": values["perp_volume"],
                "perp_taker_volume": values["perp_taker_volume"],
                "perp_maker_volume": values["perp_maker_volume"],
                "total_fee": values["total_fee"],
                "broker_fee": values["broker_fee"],
                "address": values["address"],
                "broker_id": values["broker_id"],
                "realized_pnl": values["realized_pnl"],
            })

        # Step 2: Async upsert
        async for db in get_db():
            try:
                stmt = insert(TVolumeRecord).values(records)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["date", "account_id"],
                    set_={
                        "perp_volume": stmt.excluded.perp_volume,
                        "perp_taker_volume": stmt.excluded.perp_taker_volume,
                        "perp_maker_volume": stmt.excluded.perp_maker_volume,
                        "total_fee": stmt.excluded.total_fee,
                        "broker_fee": stmt.excluded.broker_fee,
                        "address": stmt.excluded.address,
                        "broker_id": stmt.excluded.broker_id,
                        "realized_pnl": stmt.excluded.realized_pnl,
                    }
                )
                await db.execute(stmt)
                await db.commit()

                logger.info(f"✅ Upserted {len(records)} grouped records")
                return {"rows": records}

            except Exception as e:
                await db.rollback()
                logger.error(f"Database error: {str(e)}")
                return None

    except requests.RequestException as e:
        logger.error(f"HTTP error fetching data: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None


async def run_periodically(interval_hours=1):
    """Run the fetch function periodically every interval_hours."""
    while True:
        try:
            logger.info(f"Starting fetch at {datetime.datetime.now()}")
            result = await fetch_broker_daily_volume_orderly()
            if result:
                logger.info(f"✅ Successfully processed {len(result.get('rows', []))} records")
            else:
                logger.warning("⚠️ No data received from API")
        except Exception as e:
            logger.error(f"❌ Error in periodic fetch: {str(e)}")

        logger.info(f"⏳ Waiting {interval_hours} hour(s) until next run...")
        await asyncio.sleep(interval_hours * 3600)
