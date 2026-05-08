import asyncio
import httpx

BASE_URL = "https://hacker-news.firebaseio.com/v0"
SEMAPHORE = asyncio.Semaphore(50)

async def fetch_item(client: httpx.AsyncClient, item_id: int) -> dict | None:
    async with SEMAPHORE:
        r = await client.get(f"{BASE_URL}/item/{item_id}.json")
        if r.status_code != 200:
            return None
        return r.json()

async def fetch_top_story_ids(client: httpx.AsyncClient) -> list[int]:
    r = await client.get(f"{BASE_URL}/topstories.json")
    if r.status_code != 200:
        return []
    return r.json()