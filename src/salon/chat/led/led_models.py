

from typing import Literal
from pydantic import BaseModel, Field
from enum import Enum


class LedClass(Enum):
    main = "main"
    secondary = "secondary"
    ambient = "ambient"

class LedColor(Enum):
    # Native colors for strips
    red = "red"
    green = "green"
    blue = "blue"
    black = "black"
    white = "white"
    purple = "purple"
    yellow = "yellow"
    cyan = "cyan"
    # Others, to be mapped
    pink = "pink"
    orange = "orange"
    brown = "brown"
    grey = "grey"
    magenta = "magenta"
    turquoise = "turquoise"
    gold = "gold"
    silver = "silver"
    violet = "violet"
    indigo = "indigo"
    maroon = "maroon"
    olive = "olive"
    lime = "lime"
    teal = "teal"
    navy = "navy"
    beige = "beige"
    lavender = "lavender"
    amber = "amber"
    fuchsia = "fuchsia"

    def to_api_color(self) -> str:
        match self:
            case LedColor.red | LedColor.magenta | LedColor.brown | LedColor.maroon:
                return "red"
            case LedColor.green | LedColor.olive | LedColor.lime:
                return "green"
            case LedColor.blue | LedColor.navy:
                return "blue"
            case LedColor.black:
                return "black"
            case LedColor.white | LedColor.grey | LedColor.silver | LedColor.beige:
                return "white"
            case LedColor.purple | LedColor.violet | LedColor.indigo | LedColor.lavender | LedColor.pink  | LedColor.fuchsia:
                return "purple"
            case LedColor.yellow | LedColor.orange | LedColor.gold | LedColor.amber:
                return "yellow"
            case LedColor.cyan | LedColor.turquoise | LedColor.teal:
                return "cyan"
            case _:
                raise ValueError(f"Color {self.name} not mapped to an API color")


class ColorTime(BaseModel):
    color: LedColor = Field(description="Color to display. Use 'black' to turn off the LED.")
    time: int = Field(description="Time in milliseconds to display color. Must be greater than 0.")
    transition: Literal["solid", "fade"] = Field(description="Type of transition to use. 'solid' will instantly change to the color, 'fade' will fade to the color over the specified time.")

    def to_mqtt(self) -> str:
        return "|".join((self.color.to_api_color(), str(self.time), self.transition))


class ColorPattern(BaseModel):
    colors: list[ColorTime] = Field(description=(
        "Colors to display. Will loop through this list, "
        "displaying each color for the specified time. "
        "Time does not matter for a list of length 1."
    ))

    def to_mqtt(self) -> str:
        return ";".join((c.to_mqtt() for c in self.colors))
