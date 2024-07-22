from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./eartalk.db"

    # 60 minutes * 24 hours * 365 days = 365 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365
    SECRET_KEY: str = "3c330b907b36e17beb65996b0810956ffe5303c232f0e892226122fb3bb2c572"

    AUDIO_DIR_NAME: str = "audio_files"
    AUDIO_DIR: str = "/audio_files/"
    ORIGINAL_AUDIO_DIR: str = "/audio_files/original/"
    PROCESSED_AUDIO_DIR: str = "/audio_files/processed/"


settings = Settings()  # type: ignore
