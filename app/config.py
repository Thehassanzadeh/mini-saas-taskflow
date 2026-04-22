from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any

APP_DIR = Path(__file__).resolve().parents[0]  # .../app


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALG: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SMS_IR_API_KAY_OTP: str
    LINE_NUMBER_OTP: int
    OTP_TEMPLATE_ID: int
    OTP_EXPIRE_MINUTES: int

    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# for run:
# uv run alembic revision --autogenerate -m "your description"
# uv run alembic upgrade head
