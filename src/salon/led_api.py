from enum import Enum

from pydantic import BaseModel, Field


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

