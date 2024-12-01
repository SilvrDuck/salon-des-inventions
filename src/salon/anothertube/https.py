import httpx
from urllib.error import HTTPError
from salon.anothertube.errors import TooManyRequests, InvalidURL, AIOError

async def request(url: str):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " 
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/107.0.0.0 Safari/537.36"
        ),
    }

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            return resp.text
    except HTTPError as e:
        if e.code == 404:
            raise InvalidURL('can not find anything with the requested url')
        if e.code == 429:
            raise TooManyRequests('you are being rate-limited for sending too many requests')
    except Exception as e:
        raise AIOError(f'{e!r}') from None
