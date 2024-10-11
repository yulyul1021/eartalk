import os

from dotenv import load_dotenv

from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str = os.getenv('SQLALCHEMY_DATABASE_URL')

    # 60 minutes * 24 hours * 365 days = 365 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 365
    SECRET_KEY: str = os.getenv('SECRET_KEY')

    SMTP_SSL_PORT:          int = 465  # SSL connection
    SMTP_SERVER:            str = os.getenv('SMTP_SERVER')
    SENDER_EMAIL:           str = os.getenv('SENDER_EMAIL')
    SENDER_PASSWORD:        str = os.getenv('SENDER_PASSWORD')

    AI_REQUEST_URL:         str = os.getenv('AI_REQUEST_URL')
    MEDIA_URL:              str = os.getenv('MEDIA_URL')

    MEDIA_DIR:              str = os.getenv('MEDIA_DIR')
    # AUDIO_ROOT:             str = os.getenv('AUDIO_ROOT')
    LOGFILE_ROOT:           str = os.getenv('LOGFILE_ROOT')
    DEFAULT_REF_AUDIO_DIR:  str = os.getenv('DEFAULT_REF_AUDIO_DIR')


settings = Settings()  # type: ignore
