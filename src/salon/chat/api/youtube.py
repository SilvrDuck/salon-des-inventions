import asyncio
import time

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.anothertube.search import search_videos_with_metadata
from salon.config import config

YT_API = "https://www.googleapis.com/youtube/v3/"
class GetYoutubeLinkArgs(BaseModel):
    _max_queries = 6
    queries: list[str] = Field(description=f"List of YouTube search queries, max {_max_queries} queries", max_items=_max_queries)

class VideoId(BaseModel):
    video_id: str = Field(description="YouTube video id, e.g. 'dQw4w9WgXcQ'")

    def to_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

class VideoIdList(BaseModel):
    video_ids: list[VideoId] = Field(description="List of YouTube video ids")

    def to_urls(self):
        return [vid.to_url() for vid in self.video_ids]


async def _aget_ids_videos_for_query(query: str, n=10) -> list[str]:
    url = f"{YT_API}search?part=snippet&maxResults={n}&q={query}&key={config.youtube_api_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return [
        item["id"]["videoId"]
        for item in data["items"]
        if item["id"]["kind"] == "youtube#video"
    ]

async def _aget_video_info(vidcodes: list[str]) -> dict:
    ids = ",".join(vidcodes)
    parts = "&part=contentDetails&part=snippet"
    url = f"{YT_API}videos?id={ids}{parts}&key={config.youtube_api_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()

def _afilter_relevant_info(info: dict) -> dict:
    items = info["items"]
    return {
        item["id"]: {
            "title": item["snippet"].get("title", ""),
            "description": item["snippet"].get("description", ""),
            "channelTitle": item["snippet"].get("channelTitle", ""),
            "tags": item["snippet"].get("tags", []),
            "duration": item["contentDetails"].get("duration", ""),
        }
        for item in items
    }



async def _aget_video_info_from_query(query: str) -> dict:
    video_ids = await _get_ids_videos_for_query(query)
    info = await _get_video_info(video_ids)
    return _afilter_relevant_info(info)


def _extract_relevant_info(videos) -> dict:
    return {
        (meta := video.metadata)["id"]: {
            "title": meta.get("title", ""),
            "views": meta.get("views", ""),
            "duration": meta.get("duration", ""),
            "upload_date": meta.get("upload_date", ""),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "genre": meta.get("genre", ""),
        }
        for video in videos
    }


async def aget_youtube_video_suggestions(update: GetYoutubeLinkArgs) -> dict:
    update = GetYoutubeLinkArgs(**update)
    tasks = [_get_video_info_from_query(query) for query in update.queries]
    return await asyncio.gather(*tasks)


def throttle(val: any, *, ms: int, idx: int=1) -> any:
    """Slows down requests to the YouTube API to avoid rate limiting,
    idx allows to skip waiting for the first request"""
    if idx > 0:
        time.sleep(ms / 1000)
    return val

def _get_ids_videos_for_query(query: str, n=10) -> list[str]:
    results = aiotube.Search.videos(query, limit=n)
    return [throttle(AiotubeVideo(res), ms=10, idx=i) for i, res in enumerate(results)]


async def _get_video_info_from_query(query: str) -> dict:
    return  await search_videos_with_metadata(
        query,
        fields=[
            "id",
            "title",
            "views",
            "duration",
            "upload_date",
            "description",
            "tags",
            "genre",
        ],
    )


async def get_youtube_video_suggestions(update: GetYoutubeLinkArgs) -> dict:
    update = GetYoutubeLinkArgs(**update)
    return [await _get_video_info_from_query(query) for query in update.queries]


youtubeLinkTool = StructuredTool.from_function(
    coroutine=get_youtube_video_suggestions,
    name="GetYoutubeLink",
    description="Get YouTube links from search queries",
    args_schema=GetYoutubeLinkArgs,
    return_direct=True,
)
