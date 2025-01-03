import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from app.controllers.TLoginController import router as tlogin_router
from app.controllers.TSignalController import router as tsignal_router
from app.controllers.TrainingInProgressController import router as training_router
from app.controllers.TBotStatusController import router as t_bot_status_router
from app.controllers.BinanceController import router as binance_router

app = FastAPI()

# Include the routers
app.include_router(tlogin_router, prefix="/api/v1", tags=["TLogin"])
app.include_router(tsignal_router, prefix="/api/v1", tags=["TSignal"])
app.include_router(training_router, prefix="/api/v1", tags=["TrainingInProgress"])
app.include_router(t_bot_status_router, prefix="/api/v1", tags=["TBotStatus"])
app.include_router(binance_router, prefix="/api/v1", tags=["Binance"])

# run update of tables
# alembic revision --autogenerate -m "initial tables"
# commit
# alembic upgrade head
# Run project
# uvicorn app.main:app --reload
# redis-cli flushdb
# redis-cli flushall