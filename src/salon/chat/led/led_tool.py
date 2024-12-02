import asyncio

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.chat.led.led_api import set_led
from salon.chat.led.led_models import ColorPattern, LedClass


class PostLedUpdateArgs(BaseModel):
    main_led: ColorPattern = Field(description="Main LED")
    secondary_led: ColorPattern = Field(description="Secondary LED")
    ambient_led: ColorPattern = Field(description="Ambient LED")

async def post_led_update(update: PostLedUpdateArgs) -> str:
    update = PostLedUpdateArgs(**update)

    await asyncio.gather(
        set_led(LedClass.main, update.main_led),
        set_led(LedClass.secondary, update.secondary_led),
        set_led(LedClass.ambient, update.ambient_led),
    )

    return str(update)

ledUpdateTool = StructuredTool.from_function(
    coroutine=post_led_update,
    name="LedUpdate",
    description="Update LED colors",
    args_schema=PostLedUpdateArgs,
    return_direct=True,
)