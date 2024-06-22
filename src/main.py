import hashlib
import logging
import string

from databases import Database
from fastapi import FastAPI, HTTPException, Depends
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
app = FastAPI()

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
    logger.info(f"Received URL to encode: {url.original_url}")
    try:
        # Check if the original URL already exists in the database
        result = await db.execute(select(URL).filter(URL.original_url == url.original_url))
        existing_url = result.scalars().first()
        if existing_url:
            logger.info(f"URL already exists: {existing_url.short_url}")
            return ShortURLModel(short_url=f"http://short.est/{existing_url.short_url}")

        # Generate short URL if it does not exist
        short_url = generate_short_url(url.original_url)
        logger.info(f"Generated short URL: {short_url}")
        db_url = URL(original_url=url.original_url, short_url=short_url)
        db.add(db_url)
        await db.commit()
        await db.refresh(db_url)
        logger.info(f"URL successfully encoded and stored: {db_url.id}")
        return ShortURLModel(short_url=f"http://short.est/{short_url}")
    except Exception as e:
        logger.error(f"Error encoding URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decode/", response_model=URLModel)
async def decode_url(short_url: ShortURLModel, db: AsyncSession = Depends(get_db)):
    """
    Endpoint to decode a shortened URL to its original URL.

    :param short_url: ShortURLModel object containing the shortened URL.
    :param db: Database session.
    :return: URLModel object containing the original URL.
    """
    logger.info(f"Received short URL to decode: {short_url.short_url}")
    try:
        # Validate that the short URL matches the expected format
        if not short_url.short_url.startswith("http://short.est/"):
            logger.warning(f"Invalid short URL format: {short_url.short_url}. "
                           f"The URL must start with http://short.est/.")
            raise HTTPException(status_code=400, detail="Invalid short URL format")

        # Extract the Base62 part from the shortened URL
        url_id_str = short_url.short_url.split('/')[-1]

        # Check if the shortened URL exists in the database
        query = select(URL).where(URL.short_url == url_id_str)
        result = await db.execute(query)
        db_url = result.scalars().first()

        if db_url is None:
            logger.warning(f"Short URL not found: {short_url.short_url}")
            raise HTTPException(status_code=404, detail="Short URL not found")

        logger.info(f"Short URL decoded successfully: {db_url.original_url}")
        return URLModel(original_url=db_url.original_url)
    except Exception as e:
        logger.error(f"Error decoding URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))
