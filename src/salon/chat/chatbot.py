import asyncio
from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI

from salon.chat.led.led_tool import ledUpdateTool
from salon.chat.youtube.yt_tool import VideoIdList, youtubeLinkTool
from salon.chat.prompts import (
    LED_SUBSYSTEM,
    YOUTUBE_SELECTOR_SUBSUBSYSTEM,
    YOUTUBE_SUBSYSTEM,
)
from salon.config import config

llm = ChatOpenAI(model="gpt-4o", api_key=config.openai_api_key)


llm_tools = llm.bind_tools([ledUpdateTool], tool_choice=ledUpdateTool.name)
llm_youtube = llm.bind_tools([youtubeLinkTool], tool_choice=youtubeLinkTool.name)

led_chain = llm_tools | (lambda x: x.tool_calls[0]["args"]) | ledUpdateTool.coroutine
youtube_chain = llm_youtube | (lambda x: x.tool_calls[0]["args"]) | youtubeLinkTool.coroutine
llm_youtube_id = llm.with_structured_output(VideoIdList)


async def _led_response(msg: ChatMessage) -> str:
    return str(await led_chain.ainvoke([LED_SUBSYSTEM, msg]))

async def _youtube_response(msg: ChatMessage) -> str:
    youtube_results = str(await youtube_chain.ainvoke([YOUTUBE_SUBSYSTEM, msg]))
    youtube_list_msg = ChatMessage(role="assistant", content=youtube_results)
    youtube_video_ids = await llm_youtube_id.ainvoke([YOUTUBE_SELECTOR_SUBSUBSYSTEM, youtube_list_msg, msg])
    return "\n".join(youtube_video_ids.to_urls())


async def get_response(text) -> str:
    msg = ChatMessage(role="user", content=text)

    results = await asyncio.gather(
        _led_response(msg),
        _youtube_response(msg),
    )
    return "\n\n".join(results)
