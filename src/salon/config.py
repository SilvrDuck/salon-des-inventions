from pydantic_settings import BaseSettings


class Config(BaseSettings):

    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    
    # Auto consumed by langchain
    langchain_tracing_v2: str = "__set_in_dotenv__"
    langchain_endpoint: str = "__set_in_dotenv__"
    langchain_api_key: str = "__set_in_dotenv__"
    langchain_project: str = "__set_in_dotenv__"

    # Youtube API
    youtube_api_key: str = "__set_in_dotenv__"

    # Openai
    openai_api_key: str = "__set_in_dotenv__"

config = Config(_env_file='.env', _env_file_encoding='utf-8')
