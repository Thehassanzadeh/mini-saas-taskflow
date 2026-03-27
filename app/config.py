from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parents[1]  # .../app


class Settings(BaseSettings):
    SQLALCHEMY_DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


# for run:
# uv run alembic revision --autogenerate -m "your description"
# uv run alembic upgrade head
