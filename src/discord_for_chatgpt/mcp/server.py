from typing import Any, Optional

from fastapi import FastAPI
from mcp.server.mcpserver import MCPServer

from ..config import settings
from ..discord.client import get_discord_client
from ..identity.sessions import session_manager

mcp = MCPServer(settings.mcp_server_name)


@mcp.tool(
    name="discord_get_identity",
    description="Get the authenticated Discord user's identity and essential details.",
)
async def discord_get_identity(session_token: Optional[str] = None) -> dict[str, Any]:
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    try:
        client = get_discord_client(bot=False)
        identity = await client.get_current_user()
        return {
            "id": identity.get("id"),
            "username": identity.get("username"),
            "discriminator": identity.get("discriminator"),
            "avatar": identity.get("avatar"),
            "email": identity.get("email"),
            "global_name": identity.get("global_name"),
        }
    except Exception as e:
        return {
            "id": user.discord_id,
            "username": user.username,
            "error": f"Could not fetch live identity: {str(e)}",
        }


@mcp.tool(
    name="discord_list_guilds",
    description="List Discord servers (guilds) accessible to the authenticated identity or bot as permitted.",
)
async def discord_list_guilds(session_token: Optional[str] = None) -> dict[str, Any]:
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    try:
        client = get_discord_client(bot=False)
        guilds = await client.get_user_guilds()
        return {"guilds": guilds}
    except Exception as e:
        try:
            client = get_discord_client(bot=True)
            guilds = await client.get_user_guilds()
            return {"guilds": guilds}
        except Exception:
            raise ValueError(f"Cannot list guilds: {str(e)}. Ensure proper OAuth scopes or bot configuration.")


@mcp.tool(
    name="discord_list_channels",
    description="List channels in a guild. Requires access to the guild.",
)
async def discord_list_channels(guild_id: str, session_token: Optional[str] = None) -> dict[str, Any]:
    if not guild_id:
        raise ValueError("guild_id is required")
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    try:
        client = get_discord_client(bot=False)
        channels = await client.get_guild_channels(guild_id)
        return {"guild_id": guild_id, "channels": channels}
    except Exception as e:
        try:
            client = get_discord_client(bot=True)
            channels = await client.get_guild_channels(guild_id)
            return {"guild_id": guild_id, "channels": channels}
        except Exception:
            raise ValueError(f"Cannot list channels: {str(e)}. Check permissions and bot membership.")


@mcp.tool(
    name="discord_get_channel",
    description="Get detailed information about a specific channel if accessible.",
)
async def discord_get_channel(channel_id: str, session_token: Optional[str] = None) -> dict[str, Any]:
    if not channel_id:
        raise ValueError("channel_id is required")
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    try:
        client = get_discord_client(bot=False)
        channel = await client.get_channel(channel_id)
        return channel
    except Exception as e:
        try:
            client = get_discord_client(bot=True)
            channel = await client.get_channel(channel_id)
            return channel
        except Exception:
            raise ValueError(f"Cannot get channel: {str(e)}. Check permissions.")


@mcp.tool(
    name="discord_read_messages",
    description="Read messages from a channel within permission limits. Supports pagination via limit.",
)
async def discord_read_messages(channel_id: str, limit: int = 50, session_token: Optional[str] = None) -> dict[str, Any]:
    if not channel_id:
        raise ValueError("channel_id is required")
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    try:
        client = get_discord_client(bot=False)
        messages = await client.get_channel_messages(channel_id, limit=limit)
        return {"channel_id": channel_id, "messages": messages}
    except Exception as e:
        try:
            client = get_discord_client(bot=True)
            messages = await client.get_channel_messages(channel_id, limit=limit)
            return {"channel_id": channel_id, "messages": messages}
        except Exception:
            raise ValueError(f"Cannot read messages: {str(e)}. Check channel permissions.")


@mcp.tool(
    name="discord_search_messages",
    description="Search messages if supported. Not all Discord API contexts support global search via bot/user tokens; limitations may apply.",
)
async def discord_search_messages(query: str, guild_id: Optional[str] = None, session_token: Optional[str] = None) -> dict[str, Any]:
    if not query:
        raise ValueError("query is required")
    if not session_token:
        raise ValueError("Authentication required")
    user = await session_manager.validate_session(session_token)
    if not user:
        raise ValueError("Invalid or expired session")
    raise ValueError("Message search not available with configured API permissions in this environment. Requires specific Discord search capabilities or different auth context.")


# Mount the MCP app
try:
    mcp_app = mcp.streamable_http_app()
except Exception:
    mcp_app = FastAPI()
