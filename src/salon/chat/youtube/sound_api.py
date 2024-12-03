import httpx

from salon.config import config


async def play_videos(video_ids: list[str]):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{config.sound_player_connection}/play", json={"video_ids": video_ids})
        response.raise_for_status()
        return response.json()
    
async def stop_videos():
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{config.sound_player_connection}/stop")
        response.raise_for_status()
        return response.json()
