import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from src.main import app  # <-- ДОДАНО ІМПОРТ APP


@pytest.mark.asyncio
async def test_health_check():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
        ) as ac:
            response = await ac.get("/health")

    assert response.status_code == 200