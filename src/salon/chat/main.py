import gradio as gr

from salon.chat import chatbot
from salon.config import config

_ = config  # side effect env var reads for langsmith


async def get_response(text):
    response = await chatbot.get_response(text)
    print(response)
    return None


TITLE = "Super Invention 3000™"
theme = gr.Theme.from_hub("YTheme/Minecraft")
css = "footer {visibility: hidden}"


def register_submit_event(event):
    """Deals with freezing the interface while the bot is thinking."""
    (
        event(fn=lambda: gr.update(interactive=False), inputs=None, outputs=btn)
        .then(fn=get_response, inputs=textbox, outputs=textbox)
        .then(fn=lambda: gr.update(interactive=True), inputs=None, outputs=btn)
    )


with gr.Blocks(title=TITLE, theme=theme, css=css) as demo:

    gr.Markdown(f"# {TITLE}")

    textbox = gr.Textbox(
        label="Quelle ambiance voulez vous vivre ?",
        placeholder="Décrivez ici une expérience, un sentiment, un rêve…",
        lines=5,
    )
    btn = gr.Button("C’est parti !", variant="primary")

    # Apply the same chain to both button click and textbox submit
    register_submit_event(btn.click)
    register_submit_event(textbox.submit)

print("Starting the invention...")
demo.launch(show_api=False)
