import asyncio
import time

import aiotube.https
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
    return await asyncio.gather(*(
            _get_video_info_from_query(query)
            for query in update.queries
        )
    )


youtubeLinkTool = StructuredTool.from_function(
    coroutine=get_youtube_video_suggestions,
    name="GetYoutubeLink",
    description="Get YouTube links from search queries",
    args_schema=GetYoutubeLinkArgs,
    return_direct=True,
)
