import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.config import config

YT_API = "https://www.googleapis.com/youtube/v3/"
class GetYoutubeLinkArgs(BaseModel):
    query: str = Field(description="Youtube search query")

class VideoId(BaseModel):
    video_id: str = Field(description="Youtube video id, e.g. 'dQw4w9WgXcQ'")

    def to_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"


def _get_ids_videos_for_query(query: str, n=10) -> list[str]:
    url = f"{YT_API}search?part=snippet&maxResults={n}&q={query}&key={config.youtube_api_key}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    return [item["id"]["videoId"] for item in data["items"]]

def _get_video_info(vidcodes: list[str]) -> dict:
    ids = ",".join(vidcodes)
    url = f"{YT_API}videos?id={ids}&part=contentDetails&key={config.youtube_api_key}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_youtube_video_suggestions(update: GetYoutubeLinkArgs) -> str:

    video_ids = _get_ids_videos_for_query(update.query)
    video_infos = _get_video_info(video_ids)

    return video_infos

youtubeLinkTool = StructuredTool.from_function(
    func=get_youtube_video_suggestions,
    name="GetYoutubeLink",
    description="Get youtube link from search query",
    args_schema=GetYoutubeLinkArgs,
    return_direct=True,
)