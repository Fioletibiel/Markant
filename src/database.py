"""
Database module for the URL shortening service.
"""

from databases import Database
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL for SQLite with aiosqlite driver
DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Initialize the Database object for asynchronous operations
database = Database(DATABASE_URL)

# Base class for declarative class definitions
Base = declarative_base()


class URL(Base):
    """
    URL model to store original and shortened URLs.

    Attributes:
        id (int): Primary key.
        original_url (str): The original URL.
        short_url (str): The shortened URL.
    """
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, unique=True, index=True)
    short_url = Column(String, unique=True, index=True)


# Create an asynchronous engine
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a configured "AsyncSession" class
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """
    Initializes the database by creating tables if they don't exist.
    """
    async with async_engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
