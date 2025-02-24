import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    POSTGRES_URL: str = os.getenv("POSTGRES_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")


settings = Settings()
