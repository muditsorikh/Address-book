from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    app_name: str = "Address Book API"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str = "sqlite:///./address_book.db"
    log_level: str = "INFO"

    model_config = {"env_prefix": "ADDRESSBOOK_", "env_file": ".env"}


settings = Settings()
