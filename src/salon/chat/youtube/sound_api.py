from salon.config import config
from salon.sound.models import PlayRequest, StopRequest, SOUND_TOPIC
from aiomqtt import Client as MQTT


async def play_videos(video_ids: list[str]) -> None:
    play_request = PlayRequest(video_ids=video_ids)
    async with MQTT(config.mqtt_host, config.mqtt_port) as client:
        await client.publish(SOUND_TOPIC, play_request.model_dump_json(), retain=True)


async def stop_videos():
    stop_request = StopRequest(stop=True)
    async with MQTT(config.mqtt_host, config.mqtt_port) as client:
        await client.publish(SOUND_TOPIC, stop_request.model_dump_json(), retain=True)
