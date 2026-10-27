from typing import Any, Optional

import httpx

from ..config import settings

DISCORD_API_BASE = "https://discord.com/api/v10"


class DiscordAPIClient:
    def __init__(self, token: Optional[str] = None, bot: bool = False) -> None:
        self.token = token or settings.discord_bot_token
        self.bot = bot

    def _headers(self) -> dict[str, str]:
        if self.bot and self.token:
            return {"Authorization": f"Bot {self.token}", "Content-Type": "application/json"}
        if self.token:
            return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        return {"Content-Type": "application/json"}

    async def get_current_user(self) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCORD_API_BASE}/users/@me", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_user_guilds(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_guild_channels(self, guild_id: str) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCORD_API_BASE}/guilds/{guild_id}/channels", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_channel(self, channel_id: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{DISCORD_API_BASE}/channels/{channel_id}", headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> list[dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{DISCORD_API_BASE}/channels/{channel_id}/messages?limit={limit}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return resp.json()


def get_discord_client(token: Optional[str] = None, bot: bool = False) -> DiscordAPIClient:
    return DiscordAPIClient(token=token, bot=bot)
