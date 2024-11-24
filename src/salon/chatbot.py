from langchain_core.messages import ChatMessage

from langchain_openai import ChatOpenAI

from salon.apis.led import ledUpdateTool

llm = ChatOpenAI(model="gpt-4o")


llm_led = llm.bind_tools([ledUpdateTool], tool_choice=ledUpdateTool.name)

chain = llm_led | (lambda x: x.tool_calls[0]["args"]) | ledUpdateTool.func

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
