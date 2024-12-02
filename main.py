from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
import httpx
import random
import string
import os
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from cachetools import TTLCache
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

tags_cache = TTLCache(maxsize=100, ttl=3600)
video_cache = TTLCache(maxsize=1000, ttl=1800)

http_client = None

class VideoInfo(BaseModel):
    title: str
    tag: str
    stream_url: str
    cover_url: str

class TagResponse(BaseModel):
    text: str
    url: str

class ErrorResponse(BaseModel):
    detail: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        headers={
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    )
    yield
    await http_client.aclose()

app = FastAPI(
    title="Hanime.tv API",
    description="API for accessing Hanime.tv content",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

async def generate_random_signature():
    return ''.join(random.choices(string.hexdigits, k=64))

async def json_gen(url: str) -> dict:
    headers = {
        'X-Signature-Version': 'web2',
        'X-Signature': await generate_random_signature(),
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = await http_client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing JSON response: {str(e)}"
        )

async def get_video_info(video_id: int, cover_url: Optional[str] = None) -> Optional[VideoInfo]:
    cache_key = f"video_{video_id}"
    if cache_key in video_cache:
        return video_cache[cache_key]

    video_api_url = f'https://hanime.tv/api/v8/video?id={video_id}'
    video_data = await json_gen(video_api_url)

    if not video_data.get('videos_manifest') or not video_data['videos_manifest']['servers']:
        return None

    streams = video_data['videos_manifest']['servers'][0].get('streams', [])
    stream_720p = next((s for s in streams if s.get('height') == "720"), None)

    if not stream_720p:
        return None

    first_tag = (video_data.get('hentai_tags') or [{'text': 'No Tag'}])[0]['text']
    video_info = VideoInfo(
        title=video_data.get('hentai_video', {}).get('name', f'Video {video_id}'),
        tag=first_tag,
        stream_url=stream_720p.get('url', ''),
        cover_url=cover_url or video_data.get('hentai_video', {}).get('cover_url', '')
    )
    video_cache[cache_key] = video_info
    return video_info

@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Hanime.tv API",
        "endpoints": {
            "tags": "/tags",
            "tag_videos": "/tags/{tag}?page=1&limit=10",
            "trending": "/trending/{time}?page=1&limit=10"
        }
    }

@app.get("/tags", response_model=List[TagResponse], tags=["tags"])
async def get_tags():
    if 'tags' in tags_cache:
        return tags_cache['tags']

    browse_url = 'https://hanime.tv/api/v8/browse'
    data = await json_gen(browse_url)

    if not data.get('hentai_tags'):
        raise HTTPException(status_code=404, detail="No tags found")

    tags = [
        TagResponse(text=tag['text'], url=f"/tags/{tag['text']}")
        for tag in data['hentai_tags']
    ]
    tags_cache['tags'] = tags
    return tags

@app.get("/tags/{tag}", response_model=List[VideoInfo], tags=["videos"])
async def get_videos_by_tag(tag: str, page: int = 1, limit: int = 24):
    browse_url = f'https://hanime.tv/api/v8/browse/hentai-tags/{tag}?page={page}&order_by=views&ordering=desc'
    browse_data = await json_gen(browse_url)

    if not browse_data.get('hentai_videos'):
        return []

    videos = browse_data['hentai_videos'][:limit]
    tasks = [get_video_info(video['id'], video.get('cover_url')) for video in videos]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_results = [
        result for result in results if isinstance(result, VideoInfo)
    ]
    return valid_results

@app.get("/trending/{time}", response_model=List[VideoInfo], tags=["videos"])
async def get_trending(time: str = "day", page: int = 1, limit: int = 24):
    if time not in ["day", "week", "month", "year"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid time parameter. Must be: day, week, month, or year"
        )

    browse_url = f'https://hanime.tv/api/v8/browse-trending?time={time}&page={page}&order_by=views&ordering=desc'
    browse_data = await json_gen(browse_url)

    if not browse_data.get('hentai_videos'):
        return []

    videos = browse_data['hentai_videos'][:limit]
    tasks = [get_video_info(video['id'], video.get('cover_url')) for video in videos]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    valid_results = [
        result for result in results if isinstance(result, VideoInfo)
    ]
    return valid_results

def start():
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )

if __name__ == "__main__":
    start()
