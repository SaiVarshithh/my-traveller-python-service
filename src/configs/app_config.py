import os
from typing import Optional
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    application_name: str
    env: str

    # FastAPI app
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # DB
    db_url: str
    db_schema: str
    db_username: str
    db_password: Optional[str] = None

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_min: int = 30

    model_config = SettingsConfigDict(
        env_file=os.getenv("CONFIG_FILE_PATH", "local.config"),
        env_prefix="",
        extra="allow"
    )


_app_config_instance = None


def get_app_config() -> AppConfig:
    global _app_config_instance
    if _app_config_instance is None:
        _app_config_instance = AppConfig()
    return _app_config_instance