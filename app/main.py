import sys
import os
from fastapi import FastAPI
from app.controllers import (
    tlogin_router,
    t_bot_status_router,
    orderly_router,
    notification_router,
    auth_router
)

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI with custom docs URLs
app = FastAPI(
    title="Central API",
    description="Microservice Central API Documentation",
    version="1.0.0",
    docs_url="/api/v1/central/docs",
    redoc_url="/api/v1/central/redoc",
    openapi_url="/api/v1/central/openapi.json"
)

# Include the routers with prefixes
app.include_router(tlogin_router, prefix="/api/v1/central", tags=["TLogin"])
app.include_router(t_bot_status_router, prefix="/api/v1/central", tags=["TBotStatus"])
app.include_router(orderly_router, prefix="/api/v1/central", tags=["Orderly"])
app.include_router(notification_router, prefix="/api/v1/central", tags=["Notification"])
app.include_router(auth_router, prefix="/api/v1/central", tags=["Auth"])

# Additional configuration for OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = app.openapi()
    
    # Modify the servers section to show your gateway URL
    openapi_schema["servers"] = [
        {
            "url": "http://localhost:3000/api/v1/central",
            "description": "Local development server"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Alembic migration commands (comments)
# First time setup:
# alembic init alembic
# To create new migration:
# alembic revision --autogenerate -m "description"
# To apply migrations:
# alembic upgrade head

# Redis commands (comments)
# redis-cli flushdb
# redis-cli flushall

# Celery commands (comments)
# celery -A app.tasks.celery_app worker --loglevel=info --concurrency=2 --queues=central
# celery -A app.tasks.celery_app beat --loglevel=info