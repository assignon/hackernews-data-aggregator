import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app import hn_client


@pytest.fixture(autouse=True)
def reset_semaphore():
    hn_client._semaphore = None
    yield
    hn_client._semaphore = None


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_endpoint_1_returns_list(client):
    r = await client.get("/comments/top-stories")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) <= 50


@pytest.mark.asyncio
async def test_endpoint_2_returns_top_words(client):
    r = await client.get("/words/top-stories")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 10
    for word, count in data:
        assert isinstance(word, str)
        assert isinstance(count, int)