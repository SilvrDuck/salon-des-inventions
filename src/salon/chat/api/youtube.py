import asyncio

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.config import config

YT_API = "https://www.googleapis.com/youtube/v3/"

class GetYoutubeLinkArgs(BaseModel):
    queries: list[str] = Field(description="List of YouTube search queries")

class VideoId(BaseModel):
    video_id: str = Field(description="YouTube video id, e.g. 'dQw4w9WgXcQ'")

    def to_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

class VideoIdList(BaseModel):
    video_ids: list[VideoId] = Field(description="List of YouTube video ids")

    def to_urls(self):
        return [vid.to_url() for vid in self.video_ids]

async def _get_ids_videos_for_query(query: str, n=10) -> list[str]:
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

async def _get_video_info(vidcodes: list[str]) -> dict:
    ids = ",".join(vidcodes)
    parts = "&part=contentDetails&part=snippet"
    url = f"{YT_API}videos?id={ids}{parts}&key={config.youtube_api_key}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
    
def _filter_relevant_info(info: dict) -> dict:
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
    
async def _get_video_info_from_query(query: str) -> dict:
    video_ids = await _get_ids_videos_for_query(query)
    info = await _get_video_info(video_ids)
    return _filter_relevant_info(info)

async def get_youtube_video_suggestions(update: GetYoutubeLinkArgs) -> dict:
    update = GetYoutubeLinkArgs(**update)
    tasks = [_get_video_info_from_query(query) for query in update.queries]
    return await asyncio.gather(*tasks)

youtubeLinkTool = StructuredTool.from_function(
    coroutine=get_youtube_video_suggestions,
    name="GetYoutubeLink",
    description="Get YouTube links from search queries",
    args_schema=GetYoutubeLinkArgs,
    return_direct=True,
)