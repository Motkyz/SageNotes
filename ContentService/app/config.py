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
    AWS_REGION: str = "us-east-1"

settingS3 = SettingS3()
s3_client = boto3.client(
    "s3",
    endpoint_url=settingS3.S3_ENDPOINT,
    aws_access_key_id=settingS3.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settingS3.AWS_SECRET_ACCESS_KEY,
    region_name=settingS3.AWS_REGION,
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"})
)


class SettingKeycloak(BaseSettings):
    KEYCLOAK_URL: str
    REALM: str
    CLIENT_ID: str
    CLIENT_SECRET: str
    KEYCLOAK_AUDIENCE: str


    @property
    def issuer(self) -> str:
        return f"{self.KEYCLOAK_URL}/realms/{self.REALM}"

    @property
    def jwks_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/certs"

    @property
    def token_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/token"

    @property
    def userinfo_url(self) -> str:
        return f"{self.issuer}/protocol/openid-connect/userinfo"


settingKeycloak = SettingKeycloak()


class SettingTemporal(BaseSettings):
    TEMPORAL_HOST: str
    TEMPORAL_TASK_QUEUE: str = "content-task-queue"

settingTemporal = SettingTemporal()
