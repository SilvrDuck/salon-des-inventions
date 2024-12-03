import asyncio

from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from salon.chat.led.led_tool import ledUpdateTool
from salon.chat.prompts import (
    LED_SUBSYSTEM,
    YOUTUBE_SELECTOR_SUBSUBSYSTEM,
    YOUTUBE_SUBSYSTEM,
)
from salon.chat.youtube.yt_tool import playYoutubeTool, youtubeSuggestionsTool
from langchain_core.tools import BaseTool
from salon.config import config

llm = ChatOpenAI(model="gpt-4o", api_key=config.openai_api_key)

def _build_tool_chain(llm: BaseChatModel, tool: BaseTool):
    return  llm.bind_tools([tool], tool_choice=tool.name) | (lambda x: x.tool_calls[0]["args"]) | tool.coroutine

llm_led = _build_tool_chain(llm, ledUpdateTool)
llm_suggestion = _build_tool_chain(llm, youtubeSuggestionsTool)
llm_yt_play = _build_tool_chain(llm, playYoutubeTool)


async def _led_response(msg: ChatMessage) -> str:
    return str(await llm_led.ainvoke([LED_SUBSYSTEM, msg]))

async def _youtube_response(msg: ChatMessage) -> str:
    suggested = str(await llm_suggestion.ainvoke([YOUTUBE_SUBSYSTEM, msg]))
    suggested_msg = ChatMessage(role="assistant", content=suggested)
    played_videos = await llm_yt_play.ainvoke([YOUTUBE_SELECTOR_SUBSUBSYSTEM, suggested_msg, msg])
    return played_videos


async def get_response(text) -> str:
    msg = ChatMessage(role="user", content=text)

    results = await asyncio.gather(
        _led_response(msg),
        _youtube_response(msg),
    )
    return "\n\n".join(results)
