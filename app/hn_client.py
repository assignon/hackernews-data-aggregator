import asyncio
import httpx

BASE_URL = "https://hacker-news.firebaseio.com/v0"
_semaphore: asyncio.Semaphore | None = None

def _get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(50)
    return _semaphore

async def fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    async with _get_semaphore():
        r = await client.get(f"{BASE_URL}/item/{item_id}.json")
        if r.status_code != 200:
            return None
        return r.json()

async def fetch_top_story_ids(client: httpx.AsyncClient) -> list[int]:
    r = await client.get(f"{BASE_URL}/topstories.json")
    if r.status_code != 200:
        return []
    return r.json()