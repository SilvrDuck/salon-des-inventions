import asyncio

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.anothertube.search import search_videos_with_metadata
from salon.chat.youtube.sound_api import play_videos
from salon.chat.youtube.yt_models import VideoId


class YoutubeSuggestionsArgs(BaseModel):
    _max_queries = 6
    queries: list[str] = Field(description=f"List of YouTube search queries, max {_max_queries} queries", max_items=_max_queries)

async def _get_video_info_from_query(query: str) -> dict:
    return await search_videos_with_metadata(
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

async def get_youtube_video_suggestions(update: dict) -> dict:
    update = YoutubeSuggestionsArgs(**update)
    return await asyncio.gather(*(
            _get_video_info_from_query(query)
            for query in update.queries
        )
    )

youtubeSuggestionsTool = StructuredTool.from_function(
    coroutine=get_youtube_video_suggestions,
    name="GetYoutubeLink",
    description="Get YouTube links from search queries",
    args_schema=YoutubeSuggestionsArgs,
    return_direct=True,
)

class PlayYoutubeArgs(BaseModel):
    video_ids: list[VideoId] = Field(description="List of YouTube video ids")

async def play_youtube_videos(update: dict) -> str:
    update = PlayYoutubeArgs(**update)
    video_ids = [vid.video_id for vid in update.video_ids]
    await play_videos(video_ids)
    return "\n".join([v.to_url() for v in update.video_ids])

playYoutubeTool = StructuredTool.from_function(
    coroutine=play_youtube_videos,
    name="PlayYoutube",
    description="Play YouTube videos",
    args_schema=PlayYoutubeArgs,
    return_direct=True,
)
