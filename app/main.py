import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.controllers import (
    tlogin_router,
    tsignal_router,
    training_router,
    t_bot_status_router,
    binance_router,
    notification_router
)

app = FastAPI()


# Include the routers
app.include_router(tlogin_router, prefix="/api/v1", tags=["TLogin"])
app.include_router(tsignal_router, prefix="/api/v1", tags=["TSignal"])
app.include_router(training_router, prefix="/api/v1", tags=["TrainingInProgress"])
app.include_router(t_bot_status_router, prefix="/api/v1", tags=["TBotStatus"])
app.include_router(binance_router, prefix="/api/v1", tags=["Binance"])
app.include_router(notification_router, prefix="/api/v1", tags=["Notification"])

# run update of tables
# alembic revision --autogenerate -m "initial tables"
# commit
# alembic upgrade head
# Run project
# uvicorn app.main:app --reload
# redis-cli flushdb
# redis-cli flushall
# celery -A app.tasks.celery_app worker --loglevel=info