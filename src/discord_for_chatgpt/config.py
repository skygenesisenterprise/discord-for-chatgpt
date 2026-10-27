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


settings = Settings()
