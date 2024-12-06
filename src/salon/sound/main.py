import asyncio
from pydantic import BaseModel, ValidationError

from salon.config import config
from salon.sound.models import SOUND_TOPIC, PlayRequest, StopRequest
from salon.sound.player import Player
from aiomqtt import Client as MQTT, Message


player = Player()


def _as_model(message: str) -> BaseModel:
    for model in [PlayRequest, StopRequest]:
        try:
            validated_data = model.model_validate_json(message)
            return validated_data
        except ValidationError:
            pass  # If it doesn't match, move to the next model
    raise ValueError("No matching model found")


async def _on_mqtt_message(message: Message):
    message = message.payload.decode("utf-8")
    parsed_message = _as_model(message)
    match parsed_message:
        case PlayRequest(video_ids=video_ids):
            player.play(video_ids)
        case StopRequest(stop=True):
            player.stop()


async def main():
    async with MQTT(config.mqtt_host, config.mqtt_port) as client:
        print("Starting mqqtt")
        await client.subscribe(SOUND_TOPIC)

        async for message in client.messages:
            try:
                await _on_mqtt_message(message)
            except Exception as err:
                print(f"Error in mqtt message: {err}")


if __name__ == "__main__":
    asyncio.run(main())
