from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

llm = ChatOpenAI()

def get_response(text):
    msg = HumanMessage(text)
    return llm.invoke([msg]).content

