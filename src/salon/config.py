from pydantic_settings import BaseSettings
from salon.config import config

class Config(BaseSettings):
    # Langsmith API
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "__set__"
    langchain_api_key: str = "__set__"
    langchain_project: str = "__set__"

config = Config()
