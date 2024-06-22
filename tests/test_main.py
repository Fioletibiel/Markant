"""
This module contains tests for the URL shortening service.

It includes tests for the following endpoints:
- /encode/: Encodes a URL to a shortened URL.
- /decode/: Decodes a shortened URL back to the original URL.

The tests cover various scenarios including:
- Successful encoding and decoding of URLs.
- Handling invalid URL formats.
- Handling non-existent shortened URLs.
"""

import pytest
from httpx import AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_encode_url():
    """
    Test the /encode/ endpoint for encoding a URL to a shortened URL.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/encode/",
            json={"original_url": "https://www.markant.com/en/"}
        )
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["short_url"].startswith("http://short.est/")
    assert data["short_url"] == "http://short.est/5FYwyk"


@pytest.mark.asyncio
async def test_decode_url():
    """
    Test the /decode/ endpoint for decoding
    a shortened URL back to the original URL.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # First, encode a URL to get a shortened URL
        encode_response = await ac.post(
            "/encode/",
            json={
                "original_url": "https://www.markant.com/en"}
        )
        assert encode_response.status_code == 200
        short_url = encode_response.json()["short_url"]

        # Now, decode the shortened URL
        decode_response = await ac.post(
            "/decode/",
            json={"short_url": short_url}
        )
        assert decode_response.status_code == 200
        data = decode_response.json()
        assert data["original_url"] == "https://www.markant.com/en"


@pytest.mark.asyncio
async def test_decode_invalid_format_url():
    """
    Test the /decode/ endpoint with an invalid URL format.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/decode/",
            json={"short_url": "http://invalid.url/abc123"}
        )
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Invalid short URL format. "
                  "The URL must start with http://short.est/."}


@pytest.mark.asyncio
async def test_decode_nonexistent_url():
    """
    Test the /decode/ endpoint with a non-existent shortened URL.
    """
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/decode/",
            json={"short_url": "http://short.est/nonexistent"}
        )
    assert response.status_code == 404
    assert response.json() == {"detail": "Short URL not found"}
