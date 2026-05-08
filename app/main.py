import asyncio
from fastapi import FastAPI
import httpx
from app.hn_client import fetch_top_story_ids, fetch_item
from app.words import top_n_words


app = FastAPI(title="HackerNews Aggregator")

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/comments/top-stories")
async def top_comments():
    async with httpx.AsyncClient(timeout=10) as client:
        story_ids = (await fetch_top_story_ids(client))[:100]
        stories = await asyncio.gather(*[fetch_item(client, id) for id in story_ids])

        comment_ids = []
        for story in stories:
            if story and story.get("kids"):
                comment_ids.extend(story["kids"])

        comment_ids = comment_ids[:50]
        comments = await asyncio.gather(*[fetch_item(client, id) for id in comment_ids])

        return [
            {"ids": c["id"], "text": c.get("text", "")} for c in comments if c and not c.get("deleted")
        ]

@app.get("/words/top-stories")
async def words_top_stories():
    async with httpx.AsyncClient(timeout=30) as client:
        story_ids = (await fetch_top_story_ids(client))[:30]
        stories = await asyncio.gather(*[fetch_item(client, id) for id in story_ids])

        comment_ids = []
        for story in stories:
            if story and story.get("kids"):
                comment_ids.extend(story["kids"])

        comment_ids = comment_ids[:100]
        comments = await asyncio.gather(*[fetch_item(client, id) for id in comment_ids])

        texts = [c['text'] for c in comments if c and c.get('text')]
        return top_n_words(texts)