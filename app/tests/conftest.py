import pytest
from httpx import AsyncClient
from app.main import app


# 提供測試用 HTTP 客戶端
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://192.168.8.121:8000") as client:
        yield client