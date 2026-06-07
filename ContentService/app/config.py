import boto3
from botocore.config import Config
from pydantic_settings import BaseSettings


class SettingPostgres(BaseSettings):
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


settingPostgres = SettingPostgres()

class SettingS3(BaseSettings):
    S3_ENDPOINT: str
    S3_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str


settingS3 = SettingS3()
s3_client = boto3.client(
    "s3",
    endpoint_url=settingS3.S3_ENDPOINT,
    aws_access_key_id=settingS3.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settingS3.AWS_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"})
)