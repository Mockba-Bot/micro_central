from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio

from app.routes import (
    status_router,
    tlogin_router,
    orderly_router,
)
from app.utils.dailyVolume import run_periodically

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(run_periodically(interval_hours=1))
    yield  # After startup
    # Optional cleanup

app = FastAPI(
    title="Crypto Trading API",
    version="1.0.0",
    description="API for running cryptocurrency Trading",
    lifespan=lifespan
)

# Routers
app.include_router(status_router, prefix="/api/v1/central", tags=["Status"])
app.include_router(tlogin_router, prefix="/api/v1/central", tags=["TLogin"])
app.include_router(orderly_router, prefix="/api/v1/central", tags=["Orderly"])

# run update of tables
# alembic init alembic solo la primera vez
# alembic revision --autogenerate -m "initial tables"
# commit
# alembic upgrade head
# Run project
# uvicorn app.main:app --reload
# redis-cli flushdb
# redis-cli flushall
# celery -A app.tasks.celery_app.celery_app worker --loglevel=warning --concurrency=2 --queues=central
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info