"""
This module sets up the test configuration for the FastAPI application,
including the creation of a test database and providing a session for testing.
"""
import collections
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.main import app
from src.main import get_db

# Add the src directory to sys.path
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'src')
))

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="module", autouse=True)
async def init_test_db():
    """
    Initializes the test database and creates the required tables.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="module")
async def db_session(init_test_db):
    """
    Provides a new database session for each test.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="module")
def client():
    """
    Provides a test client for making requests to the FastAPI application.
    """
    with TestClient(app) as c:
        yield c
