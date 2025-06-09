import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.routes import (
    status_router,
    tlogin_router,
    orderly_router,
    notification_router
)

app = FastAPI(
    title="Crypto Trading API",
    version="1.0.0",
    description="API for running cryptocurrency Trading"
)

# Include the routers
app.include_router(status_router, prefix="/api/v1/central", tags=["Status"])
app.include_router(tlogin_router, prefix="/api/v1/central", tags=["TLogin"])
app.include_router(notification_router, prefix="/api/v1/central", tags=["Notification"])
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
# celery -A app.tasks.celery_app.celery_app worker --loglevel=info --concurrency=2 --queues=central
# celery -A app.tasks.celery_app.celery_app beat --loglevel=info