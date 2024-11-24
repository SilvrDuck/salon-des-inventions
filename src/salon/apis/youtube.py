import requests
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.config import config


class GetYoutubeLinkArgs(BaseModel):
    query: str = Field(description="Youtube search query")

def get_youtube_link(update: GetYoutubeLinkArgs) -> str:
    resp = requests.get("https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=" + update["query"] + "&key=" + config.youtube_api_key)
    resp.raise_for_status()
    data = resp.json()
    print(data)
    vidcode = data["items"][0]["id"]["videoId"]
    return f"https://www.youtube.com/watch?v={vidcode}"

youtubeLinkTool = StructuredTool.from_function(
    func=get_youtube_link,
    name="GetYoutubeLink",
    description="Get youtube link from search query",
    args_schema=GetYoutubeLinkArgs,
    return_direct=True,
)