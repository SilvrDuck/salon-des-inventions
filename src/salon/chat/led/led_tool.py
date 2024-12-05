import asyncio

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from salon.chat.led.led_api import set_led
from salon.chat.led.led_models import ColorPattern, LedClass


class PostLedUpdateArgs(BaseModel):
    main_led: ColorPattern = Field(description="Main LED")
    secondary_led: ColorPattern = Field(description="Secondary LED")
    ambient_led: ColorPattern = Field(description="Ambient LED")

    @staticmethod
    def with_safe_colors(update: dict) -> "PostLedUpdateArgs":
        # The llm is very dumb and sometimes sends invalid colors
        update["main_led"] = ColorPattern.with_safe_colors(update["main_led"])
        update["secondary_led"] = ColorPattern.with_safe_colors(update["secondary_led"])
        update["ambient_led"] = ColorPattern.with_safe_colors(update["ambient_led"])
        return PostLedUpdateArgs(**update)

async def post_led_update(update: dict) -> str:
    update = PostLedUpdateArgs.with_safe_colors(update)

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
