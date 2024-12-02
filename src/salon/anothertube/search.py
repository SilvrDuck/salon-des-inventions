
import asyncio
import re
import urllib.parse

from salon.anothertube.https import request
from salon.anothertube.video_data import video_data

VIDEO_ID = re.compile("videoId\":\"(.*?)\"")

async def _find_videos(query: str) -> str:
    head = 'https://www.youtube.com/results?search_query='
    tail = '&sp=EgIQAQ%253D%253D'
    parsed_query = urllib.parse.quote_plus(query)
    return await request(head + parsed_query + tail)


async def search_videos_ids(query: str, limit: int = 10) -> list[str]:
    ids = VIDEO_ID.findall(await _find_videos(query))
    return list(set(ids))[:limit]

async def _delayed_video_data(vid: str, *, delay_ms: float = 0) -> dict:
    await asyncio.sleep(delay_ms / 1000)
    return await video_data(vid)

async def search_videos_with_metadata(query: str, fields: list[str] = None) -> list[dict]:
    """For possible fields, see the metadata method in src/salon/anothertube/video_data.py"""
    ids = await search_videos_ids(query)
    data = await asyncio.gather(*(_delayed_video_data(vid, delay_ms=i * 0) for i, vid in enumerate(ids)))

    if fields:
        return [
            {field: vid[field] for field in fields}
            for vid in data
            if vid is not None
        ]
    
    return data
