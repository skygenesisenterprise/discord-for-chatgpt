import secrets
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from ..config import settings


DISCORD_API_BASE = "https://discord.com/api/v10"
AUTH_URL = "https://discord.com/oauth2/authorize"
TOKEN_URL = f"{DISCORD_API_BASE}/oauth2/token"
USER_URL = f"{DISCORD_API_BASE}/users/@me"


class DiscordOAuth:
    def __init__(self) -> None:
        self.client_id = settings.discord_client_id
        self.client_secret = settings.discord_client_secret
        self.redirect_uri = settings.discord_redirect_uri

    def get_authorization_url(self, state: str, scopes: list[str] | None = None) -> str:
        if scopes is None:
            scopes = ["identify", "guilds"]
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
        }
        return f"{AUTH_URL}?{urlencode(params)}"

    async def exchange_code(self, code: str) -> dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as client:
            resp = await client.post(TOKEN_URL, data=data, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def get_user(self, access_token: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(USER_URL, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def get_user_guilds(self, access_token: str) -> list[dict[str, Any]]:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
            resp.raise_for_status()
            return resp.json()


oauth_client = DiscordOAuth()


def generate_state() -> str:
    return secrets.token_urlsafe(32)
