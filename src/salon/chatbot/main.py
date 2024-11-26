import gradio as gr

from salon import chatbot
from salon.config import config


def get_response(text, history):
    return chatbot.get_response(text)


demo = gr.ChatInterface(fn=get_response, type="messages")
demo.launch()
