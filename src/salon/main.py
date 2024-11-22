from salon.config import config
from salon import chatbot
import gradio as gr

def get_response(text, history):
    return chatbot.get_response(text)


demo = gr.ChatInterface(fn=get_response, type="messages")
demo.launch()