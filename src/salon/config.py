from pydantic_settings import BaseSettings


class Config(BaseSettings):
    
    # Auto consumed by langchain
    langchain_tracing_v2: str = "__set_in_dotenv__"
    langchain_endpoint: str = "__set_in_dotenv__"
    langchain_api_key: str = "__set_in_dotenv__"
    langchain_project: str = "__set_in_dotenv__"

config = Config(_env_file='.env', _env_file_encoding='utf-8')
