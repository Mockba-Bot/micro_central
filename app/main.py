import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.controllers import (
    tlogin_router,
    tsignal_router,
    t_bot_status_router,
    orderly_router,
    notification_router
)

app = FastAPI()

# Include the routers
app.include_router(tlogin_router, prefix="/api/v1/central", tags=["TLogin"])
app.include_router(tsignal_router, prefix="/api/v1/central", tags=["TSignal"])
app.include_router(t_bot_status_router, prefix="/api/v1/central", tags=["TBotStatus"])
app.include_router(orderly_router, prefix="/api/v1/central", tags=["Orderly"])
app.include_router(notification_router, prefix="/api/v1/central", tags=["Notification"])

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