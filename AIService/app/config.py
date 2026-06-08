import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)


class Settings(BaseSettings):
    yandex_cloud_api_key: str = ""
    yandex_cloud_folder: str = ""
    yandex_cloud_model: str = "yandexgpt-lite"
    summarize_temperature: float = 0.3
    summarize_max_tokens: int = 500

    class Config:
        env_file = str(env_path)
        extra = "ignore"


settings = Settings()