import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from databases import Database
from dotenv import load_dotenv
import ssl

# Load environment variables from the .env file
# Load environment variables from the specified .env file
load_dotenv(dotenv_path=".env.micro.central")

# Fetch the database URL from the environment variable
# Remove sslmode parameter from URL if present
db_url = os.getenv("DATABASE_URL")
if "sslmode=" in db_url:
    db_url = db_url.split("?")[0]
DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment or .env file.")

# Async SQLAlchemy engine
# engine = create_async_engine(DATABASE_URL, echo=True)
# SSL context for DigitalOcean PostgreSQL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Async SQLAlchemy engine with SSL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)

# Async session local
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency to get the database session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
