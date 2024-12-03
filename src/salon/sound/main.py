from fastapi import FastAPI
from pydantic import BaseModel

from salon.sound.player import Player

app = FastAPI()
player = Player()

class PlayRequest(BaseModel):
    video_ids: list[str]

@app.post("/play")
def play_videos(play_request: PlayRequest):
    player.play(play_request.video_ids)
    return {"status": "playing"}

@app.post("/stop")
def stop_videos():
    player.stop()
    return {"status": "stopped"}
