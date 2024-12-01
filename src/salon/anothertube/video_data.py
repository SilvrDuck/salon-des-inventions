
import json
import re
from typing import Any, Literal

from salon.anothertube.https import request


def metadata(data) -> dict[str, Any]:
    raise NotImplementedError("We have issues with getting dict response at some point")
    details_pattern = re.compile('videoDetails\":(.*?)\"isLiveContent\":.*?}')
    upload_date_pattern = re.compile("<meta itemprop=\"uploadDate\" content=\"(.*?)\">")
    genre_pattern = re.compile("<meta itemprop=\"genre\" content=\"(.*?)\">")
    like_count_pattern = re.compile("iconType\":\"LIKE\"},\"defaultText\":(.*?)}}")
    raw_details = details_pattern.search(data).group(0)
    upload_date = upload_date_pattern.search(data).group(1)
    metadata = json.loads(raw_details.replace('videoDetails\":', ''))
    data = {
        'title': metadata['title'],
        'id': metadata['videoId'],
        'views': metadata.get('viewCount'),
        'streamed': metadata['isLiveContent'],
        'duration': metadata['lengthSeconds'],
        'author_id': metadata['channelId'],
        'upload_date': upload_date,
        'url': f"https://www.youtube.com/watch?v={metadata['videoId']}",
        'thumbnails': metadata.get('thumbnail', {}).get('thumbnails'),
        'tags': metadata.get('keywords'),
        'description': metadata.get('shortDescription'),
    }
    try:
        likes_count = like_count_pattern.search(data).group(1)
        data['likes'] = json.loads(likes_count + '}}}')[
            'accessibility'
        ]['accessibilityData']['label'].split(' ')[0].replace(',', '')
    except (AttributeError, KeyError):
        data['likes'] = None
    try:
        data['genre'] = genre_pattern.search(data).group(1)
    except AttributeError:
        data['genre'] = None
    return data


async def video_data(video_id: str) -> str:
    url = f'https://www.youtube.com/watch?v={video_id}'
    data = await request(url)
    return metadata(data)