"""
Centralized application settings, loaded from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./credit_assistant.db"

    secret_key: str = "dev-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"

    frontend_origin: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
