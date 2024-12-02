
from aiomqtt import Client as MQTT

from salon.chat.led.led_models import ColorPattern, LedClass
from salon.config import config


TOPICS = {
    LedClass.main: "LED_MAIN",
    LedClass.secondary: "LED_SECONDARY",
    LedClass.ambient: "LED_AMBIENT",
}

async def set_led(target: LedClass, color_pattern: ColorPattern) -> None:
    async with MQTT(config.mqtt_host, config.mqtt_port) as client:
        await client.publish(TOPICS[target], color_pattern.to_mqtt())
