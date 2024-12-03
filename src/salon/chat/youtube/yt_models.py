
from pydantic import BaseModel, Field


class VideoId(BaseModel):
    video_id: str = Field(description="YouTube video id, e.g. 'dQw4w9WgXcQ'")

    def to_url(self):
        return f"https://www.youtube.com/watch?v={self.video_id}"

class VideoIdList(BaseModel):
    video_ids: list[VideoId] = Field(description="List of YouTube video ids")

    def to_urls(self):
        return [vid.to_url() for vid in self.video_ids]
