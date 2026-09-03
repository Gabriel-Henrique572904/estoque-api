from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PASTA_PROJETO = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str = (
        f"sqlite:///{(PASTA_PROJETO / 'estoque.db').as_posix()}"
    )

    model_config = SettingsConfigDict(
        env_file=PASTA_PROJETO / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()