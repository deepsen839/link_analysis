from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "AI Website Link Analysis API"
    environment: str = "development"
    llm_provider: str = "gemini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.7-flash"
    # openai_api_key: str | None = None
    # openai_model: str = "gpt-6-luna"
    request_timeout_seconds: float = 15.0
    max_html_bytes: int = 2_000_000
    max_text_chars: int = 24_000
    cache_ttl_seconds: int = 3600
    allowed_ports: str = "80,443"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings() -> Settings:
    return Settings()
