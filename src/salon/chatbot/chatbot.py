from langchain_core.messages import ChatMessage
from langchain_openai import ChatOpenAI

from salon.apis.led import ledUpdateTool
from salon.apis.youtube import VideoId, youtubeLinkTool
from salon.config import config
from salon.prompts import (
    LED_SUBSYSTEM,
    YOUTUBE_SELECTOR_SUBSUBSYSTEM,
    YOUTUBE_SUBSYSTEM,
)

llm = ChatOpenAI(model="gpt-4o", api_key=config.openai_api_key)


llm_tools = llm.bind_tools([ledUpdateTool], tool_choice=ledUpdateTool.name)
llm_youtube = llm.bind_tools([youtubeLinkTool], tool_choice=youtubeLinkTool.name)

led_chain = llm_tools | (lambda x: x.tool_calls[0]["args"]) | ledUpdateTool.func
youtube_chain = llm_youtube | (lambda x: x.tool_calls[0]["args"]) | youtubeLinkTool.func
llm_youtube_id = llm.with_structured_output(VideoId)


def get_response(text):
    msg = ChatMessage(role="user", content=text)
    led_res = str(led_chain.invoke([LED_SUBSYSTEM, msg]))
    youtube_results = str(youtube_chain.invoke([YOUTUBE_SUBSYSTEM, msg]))
    youtube_list_msg = ChatMessage(role="result_selector", content=youtube_results)
    youtube_video_id = llm.invoke([YOUTUBE_SELECTOR_SUBSUBSYSTEM, youtube_list_msg, msg])
    return led_res + "\n\n\n" + youtube_results + "\n\n\n" + youtube_video_id.to_url()
