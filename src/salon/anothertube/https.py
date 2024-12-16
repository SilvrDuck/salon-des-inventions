import httpx

from salon.anothertube.errors import AIOError, InvalidURL, TooManyRequests


client = httpx.AsyncClient(
    headers={
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/107.0.0.0 Safari/537.36"
        ),
    },
    follow_redirects=True,
)


async def request(url: str):
    try:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise InvalidURL("can not find anything with the requested url")
        if e.response.status_code == 429:
            raise TooManyRequests(
                "you are being rate-limited for sending too many requests"
            )
        raise AIOError(f"HTTP error: {e}") from None
    except Exception as e:
        raise AIOError(f"{e!r}") from None
