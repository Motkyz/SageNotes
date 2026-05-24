from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    POSTGRES_CONTENT_DB: str
    POSTGRES_CONTENT_USER: str
    POSTGRES_CONTENT_PASSWORD: str

    POSTGRES_HOST: str = "postgres_content"
    POSTGRES_PORT: int = 5432

    @property
    def db_url_asyncpg(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_CONTENT_USER}:{self.POSTGRES_CONTENT_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_CONTENT_DB}"
        )

    model_config = SettingsConfigDict(extra='ignore')

settings = Settings()