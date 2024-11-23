from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage, ChatMessage
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI

from salon.led_api import PostLedUpdateArgs, post_led_update

llm = ChatOpenAI(model="gpt-4o")


ledUpdateTool = StructuredTool.from_function(
    func=post_led_update,
    name="LedUpdate",
    description="Update LED colors",
    args_schema=PostLedUpdateArgs,
    return_direct=True,
)

llm_led = llm.bind_tools([ledUpdateTool], tool_choice="LedUpdate")

chain = llm_led | (lambda x: x.tool_calls[0]["args"]) | post_led_update

system = ChatMessage(
    role="system",
    content="""
    You are a LED ambiant control system.

    You can change the color of the LED lights in the room.

    The user will describe a mood, an ambiance, or anything really, and you will try to convey that through the LED lights.
    """,
)


def get_response(text):
    msg = ChatMessage(role="user", content=text)
    return str(chain.invoke([system, msg]))
