

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class LedClass(Enum):
    main = "main"
    secondary = "secondary"
    ambient = "ambient"

class LedColor(Enum):
    red = "red"
    green = "green"
    blue = "blue"
    black = "black"
    white = "white"
    purple = "purple"
    yellow = "yellow"
    cyan = "cyan"

    @staticmethod
    def with_safe_color(color: str) -> "LedColor":
        match color:
            case "red" | "magenta" | "brown" | "maroon":
                return LedColor.red
            case "green" | "olive" | "lime":
                return LedColor.green
            case "blue" | "navy":
                return LedColor.blue
            case "black":
                return LedColor.black
            case "white" | "grey" | "silver" | "beige":
                return LedColor.white
            case "purple" | "violet" | "indigo" | "lavender" | "pink"  | "fuchsia":
                return LedColor.purple
            case "yellow" | "orange" | "gold" | "amber":
                return LedColor.yellow
            case "cyan" | "turquoise" | "teal":
                return LedColor.cyan
            case _:
                raise ValueError(f"Color {color} cannot be safely mapped to a native color")


class ColorTime(BaseModel):
    color: LedColor = Field(description="Color to display. Use 'black' to turn off the LED.")
    time: int = Field(description="Time in milliseconds to display color. Must be greater than 0.")
    transition: Literal["solid", "fade"] = Field(description="Type of transition to use. 'solid' will instantly change to the color, 'fade' will fade to the color over the specified time.")

    @staticmethod
    def with_safe_colors(update: dict) -> "ColorTime":
        update["color"] = LedColor.with_safe_color(update["color"])
        return ColorTime(**update)

    def to_mqtt(self) -> str:
        return "|".join((self.color.value, str(self.time), self.transition))


class ColorPattern(BaseModel):
    colors: list[ColorTime] = Field(description=(
        "Colors to display. Will loop through this list, "
        "displaying each color for the specified time. "
        "Time does not matter for a list of length 1."
    ))

    @staticmethod
    def with_safe_colors(update: dict) -> "ColorPattern":
        update["colors"] = [ColorTime.with_safe_colors(c) for c in update["colors"]]
        return ColorPattern(**update)

    def to_mqtt(self) -> str:
        return ";".join((c.to_mqtt() for c in self.colors))
