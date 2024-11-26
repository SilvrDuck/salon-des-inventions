from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field
from langchain_core.tools import StructuredTool



class LedColor(Enum):
    red = "red"
    green = "green"
    blue = "blue"
    black = "black"
    white = "white"
    purple = "purple"
    yellow = "yellow"
    cyan = "cyan"

class ColorTime(BaseModel):
    color: LedColor = Field(description="Color to display. Use 'black' to turn off the LED.")
    time: int = Field(description="Time in milliseconds to display color. Must be greater than 0.")
    transation: Literal["solid", "fade"] = Field(description="Type of transition to use. 'solid' will instantly change to the color, 'fade' will fade to the color over the specified time.")

class ColorPattern(BaseModel):
    colors: list[ColorTime] = Field(description=(
        "Colors to display. Will loop through this list, "
        "displaying each color for the specified time. "
        "Time does not matter for a list of length 1."
    ))

class PostLedUpdateArgs(BaseModel):
    main_led: ColorPattern = Field(description="Main LED")
    secondary_led: ColorPattern = Field(description="Secondary LED")
    ambient_led: ColorPattern = Field(description="Ambient LED")

def post_led_update(update: PostLedUpdateArgs) -> str:
    return str(update)

ledUpdateTool = StructuredTool.from_function(
    func=post_led_update,
    name="LedUpdate",
    description="Update LED colors",
    args_schema=PostLedUpdateArgs,
    return_direct=True,
)