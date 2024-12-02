import asyncio

import gradio as gr

from salon.chat import chatbot
from salon.config import config

_ = config  # side effect env var reads for langsmith


def get_response(text, history):
    return asyncio.run(chatbot.get_response(text))


demo = gr.ChatInterface(fn=get_response, type="messages")
demo.launch()
