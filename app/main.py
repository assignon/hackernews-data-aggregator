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
    """First 50 top-level comments across the first 100 top stories."""
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
    """return the 10 most used words for the first 100 comments (again only the top level comment) for the top 30 stories. """
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

async def collect_all_comments(client: httpx.AsyncClient, story_id: int) -> list[dict]:
    story = await fetch_item(client, story_id)
    if not story:
        return []

    all_comments = []
    current_level = story.get("kids", [])
    while current_level:
        items = await asyncio.gather(*[fetch_item(client, id) for id in current_level])
        items = [i for i in items if i and not i.get("deleted") and not i.get("dead")]
        all_comments.extend(items)                                     # <-- fixed
        current_level = [kid for item in items for kid in item.get("kids", [])]
    return all_comments

@app.get("/words/all-comments")
async def words_all_comments():
    """the most used words in all comments, including nested comments, of the first 10 stories"""
    async with httpx.AsyncClient(timeout=60) as client:
        story_ids = (await fetch_top_story_ids(client))[:10]
        nested_lists = await asyncio.gather(*[collect_all_comments(client, id) for id in story_ids])

        all_comments = [c for sublist in nested_lists for c in sublist]
        texts = [c['text'] for c in all_comments if c and c.get('text')]
        return top_n_words(texts, 10)
