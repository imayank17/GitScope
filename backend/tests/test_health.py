import pytest
from httpx import AsyncClient
from app.core.config import settings


@pytest.mark.anyio
async def test_root_endpoint(client: AsyncClient):
    """
    Test that the root endpoint returns 200 OK and correct settings metadata.
    """
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["application"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert "debug" in data


@pytest.mark.anyio
async def test_health_endpoint(client: AsyncClient):
    """
    Test that the health check endpoint returns 200 OK and healthy status.
    """
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
