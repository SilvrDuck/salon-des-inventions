
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


async def search_videos_ids(query: str) -> list[str]:
    return VIDEO_ID.findall(await _find_videos(query))

async def search_videos_with_metadata(query: str, fields: list[str] = None) -> list[dict]:
    """For possible fields, see the metadata method in src/salon/anothertube/video_data.py"""
    ids = await search_videos_ids(query)
    data = await asyncio.gather(*[video_data(vid) for vid in ids])

    if fields:
        return [
            {field: vid[field] for field in fields}
            for vid in data
        ]
    
    return data
