import os
import sys
from datetime import datetime, date
import asyncio

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.database import get_db, engine
from app.models import TLogin

async def insert_user():
    async with engine.begin() as conn:
        async for db in get_db():
            new_user = TLogin(
                token=556159355,
                api_key='olWdjIsSj3PvjezNF31UJprbl3X7aVgRP5wNKGgNrSmBs612e2RcQSfZLlgPTJyU',
                api_secret='HewKJBu6Q7SM2wffCUnZWFzqtMQCGnqCECoRLdxj6PJHJAwu7i6ON1TXroIv7mcc',
                name='Andres',
                last_name='Dominguez',
                is_owner=True,
                want_signal=True,
                wallets=None,  # Use None instead of null
                creation_date=datetime.utcnow(),
                end_subscription=date(2080, 12, 31)
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            print("User inserted successfully")

if __name__ == "__main__":
    asyncio.run(insert_user())