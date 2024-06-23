"""
Main module for the URL shortening service.

This module sets up the FastAPI app and defines the API endpoints for:
- /encode/: Encodes a given URL into a shortened URL.
- /decode/: Decodes a given shortened URL back to the original URL.

It also includes:
- The database initialization.
- Utility functions for URL encoding and decoding.
"""

import hashlib
import logging
import os
import string
from contextlib import asynccontextmanager

from databases import Database
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select

from src.database import AsyncSessionLocal, init_db
from src.database import DATABASE_URL, URL
from src.models import URLModel, ShortURLModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle the lifespan events of the FastAPI application.

    This context manager handles the startup and shutdown events
    for the FastAPI application.
    During startup, it initializes the database.
    During shutdown, it disconnects from the database.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    # Startup event
    await init_db()
    yield
    # Shutdown event
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

# Mount static files
static_directory = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_directory), name="static")

# Set up templates
templates = Jinja2Templates(directory="src/templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Handle the root URL endpoint.

    This function serves the main page of the URL shortener application.
    It uses FastAPI's TemplateResponse to render the "index.html" template
    and return it as an HTML response.

    Args:
        request (Request): The request object containing
        metadata about the request.

    Returns:
        TemplateResponse: The HTML response with
        the rendered "index.html" template.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# Base62 character set
BASE62 = string.digits + string.ascii_letters

# Initialize the async engine and database
async_engine = create_async_engine(DATABASE_URL, echo=True, future=True)
database = Database(DATABASE_URL)


async def get_db():
    """
    Dependency to get a database session.
    """
    async with AsyncSessionLocal() as session:
        yield session


@app.on_event("startup")
async def startup():
    """
    Event triggered at application startup.
    Initializes the database.
    """
    await init_db()


def encode_base62(num: int) -> str:
    """
    Encodes an integer to a Base62 string.

    :param num: Integer to encode.
    :return: Encoded string in Base62 format.
    """
    if num == 0:
        return BASE62[0]
    base62 = []
    while num:
        num, rem = divmod(num, 62)
        base62.append(BASE62[rem])
    return ''.join(reversed(base62))


def generate_short_url(original_url: str) -> str:
    """
    Generates a short URL from the original URL using Base62 encoding.

    :param original_url: Original URL.
    :return: Shortened URL in Base62 format.
    """
    url_hash = hashlib.md5(original_url.encode()).hexdigest()
    hash_int = int(url_hash, 16)
    short_url = encode_base62(hash_int)
    return short_url[:6]


@app.post("/encode/", response_model=ShortURLModel)
async def encode_url(url: URLModel, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to encode an original URL to a shortened URL.

    :param url: URLModel object containing the original URL.
    :param db: Database session.
    :return: ShortURLModel object containing the shortened URL.
    """
    logger.info("Received URL to encode: %s", url.original_url)
    try:
        # Check if the original URL already exists in the database
        result = await db.execute(select(URL).filter(
            URL.original_url == url.original_url)
        )
        existing_url = result.scalars().first()
        if existing_url:
            logger.info("URL already exists: %s", existing_url.short_url)
            return ShortURLModel(
                short_url=f"http://short.est/{existing_url.short_url}"
            )

        # Generate short URL if it does not exist
        short_url = generate_short_url(url.original_url)
        logger.info("Generated short URL: %s", short_url)
        db_url = URL(original_url=url.original_url, short_url=short_url)
        db.add(db_url)
        await db.commit()
        await db.refresh(db_url)
        logger.info("URL successfully encoded and stored: %s", db_url.id)
        return ShortURLModel(short_url=f"http://short.est/{short_url}")
    except Exception as e:
        logger.error("Error encoding URL: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/decode/", response_model=URLModel)
async def decode_url(short_url: ShortURLModel,
                     db: AsyncSession = Depends(get_db)):
    """
    Endpoint to decode a shortened URL to its original URL.

    :param short_url: ShortURLModel object containing the shortened URL.
    :param db: Database session.
    :return: URLModel object containing the original URL.
    """
    logger.info("Received short URL to decode: %s", short_url.short_url)
    try:
        # Validate that the short URL matches the expected format
        if not short_url.short_url.startswith("http://short.est/"):
            logger.warning("Invalid short URL format: %s. "
                           "The URL must start with http://short.est/.",
                           short_url.short_url)
            raise HTTPException(
                status_code=400,
                detail="Invalid short URL format. "
                       "The URL must start with http://short.est/.")

        # Extract the Base62 part from the shortened URL
        url_id_str = short_url.short_url.split('/')[-1]

        # Check if the shortened URL exists in the database
        query = select(URL).where(URL.short_url == url_id_str)
        result = await db.execute(query)
        db_url = result.scalars().first()

        if db_url is None:
            logger.warning("Short URL not found: %s", short_url.short_url)
            raise HTTPException(status_code=404, detail="Short URL not found")

        logger.info("Short URL decoded successfully: %s", db_url.original_url)
        return URLModel(original_url=db_url.original_url)
    except Exception as e:
        logger.error("Error decoding URL: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e
