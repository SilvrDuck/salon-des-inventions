from pydantic import BaseModel

SOUND_TOPIC = "SOUND"


class PlayRequest(BaseModel):
    video_ids: list[str]


class StopRequest(BaseModel):
    stop: bool
