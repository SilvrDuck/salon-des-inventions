
import json
import re
from typing import Any

from salon.anothertube.https import request


def metadata(video_data) -> dict[str, Any]:
    details_pattern = re.compile('videoDetails\":(.*?)\"isLiveContent\":.*?}')
    upload_date_pattern = re.compile("<meta itemprop=\"uploadDate\" content=\"(.*?)\">")
    genre_pattern = re.compile("<meta itemprop=\"genre\" content=\"(.*?)\">")
    like_count_pattern = re.compile("iconType\":\"LIKE\"},\"defaultText\":(.*?)}}")

    raw_details = details_pattern.search(video_data).group(0)
    upload_date = upload_date_pattern.search(video_data).group(1)
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
        likes_count = like_count_pattern.search(video_data).group(1)
        data['likes'] = json.loads(likes_count + '}}}')[
            'accessibility'
        ]['accessibilityData']['label'].split(' ')[0].replace(',', '')
    except (AttributeError, KeyError):
        data['likes'] = None
    try:
        data['genre'] = genre_pattern.search(video_data).group(1)
    except AttributeError:
        data['genre'] = None
    return data


async def video_data(video_id: str) -> str | None:
    url = f'https://www.youtube.com/watch?v={video_id}'
    data = await request(url)
    try:
        return metadata(data)
    except Exception as err:
        print(f"Got exception for {video_id}: {err}")
