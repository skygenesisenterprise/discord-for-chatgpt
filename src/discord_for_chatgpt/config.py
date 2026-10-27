from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    discord_client_id: str = ""
    discord_client_secret: str = ""
    discord_redirect_uri: str = "http://localhost:8000/oauth/discord/callback"
    discord_bot_token: str = ""

    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/discord_for_chatgpt"

    secret_key: str = "change-me-in-production"
    encryption_key: str = ""
    mcp_server_name: str = "discord-for-chatgpt"
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        env = info.data.get("environment", "development")
        if env == "production" and v in ("change-me-in-production", "", "secret", "changeme"):
            raise ValueError("Insecure secret_key in production")
        return v

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str, info) -> str:
        env = info.data.get("environment", "development")
        if env == "production" and not v:
            raise ValueError("encryption_key required in production")
        return v


settings = Settings()
