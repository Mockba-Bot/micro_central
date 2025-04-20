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
                name='Andres',
                last_name='Dominguez',
                is_owner=True,
                want_signal=True,
                creation_date=datetime.utcnow(),
                language='en',
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            print("User inserted successfully")

if __name__ == "__main__":
    asyncio.run(insert_user())