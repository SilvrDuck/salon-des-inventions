from langchain_openai import ChatOpenAI
from salon_des_inventions.config import config

llm = ChatOpenAI()
llm.invoke("Hello, world!")