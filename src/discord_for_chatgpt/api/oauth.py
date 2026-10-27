import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select

from ..config import settings
from ..db.models import OAuthConnection, User
from ..db.session import AsyncSessionLocal
from ..identity.discord_oauth import generate_state, oauth_client
from ..identity.sessions import session_manager
from ..identity.token_store import token_encryption

router = APIRouter(tags=["oauth"])

# In-memory state store for simple implementation (should be persistent in prod)
_state_store = {}


@router.get("/oauth/discord/start")
async def start():
    state = generate_state()
    _state_store[state] = datetime.utcnow() + timedelta(minutes=10)
    url = oauth_client.get_authorization_url(state, scopes=["identify", "guilds"])
    return {"url": url}


@router.get("/oauth/discord/callback")
async def callback(code: str | None = None, state: str | None = None, error: str | None = None, error_description: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state")

    # Validate state
    expiry = _state_store.get(state)
    if not expiry or expiry < datetime.utcnow():
        # Clean up
        _state_store.pop(state, None)
        raise HTTPException(status_code=400, detail="Invalid or expired state")
    _state_store.pop(state, None)

    try:
        token_data = await oauth_client.exchange_code(code)
        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in")
        scope = token_data.get("scope")
        token_type = token_data.get("token_type")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed")

    try:
        discord_user = await oauth_client.get_user(access_token)
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to fetch user")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.discord_id == str(discord_user["id"])))
        user = result.scalar_one_or_none()
        if not user:
            user = User(
                discord_id=str(discord_user["id"]),
                username=discord_user.get("username"),
                discriminator=discord_user.get("discriminator"),
                avatar=discord_user.get("avatar"),
                email=discord_user.get("email"),
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

        # Store/update OAuth connection
        result = await session.execute(
            select(OAuthConnection).where(OAuthConnection.user_id == user.id, OAuthConnection.provider == "discord")
        )
        conn = result.scalar_one_or_none()
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in) if expires_in else None
        if conn:
            conn.access_token_enc = token_encryption.encrypt(access_token) if access_token else None
            conn.refresh_token_enc = token_encryption.encrypt(refresh_token) if refresh_token else None
            conn.scope = scope
            conn.expires_at = expires_at
            conn.token_type = token_type
        else:
            conn = OAuthConnection(
                user_id=user.id,
                provider="discord",
                access_token_enc=token_encryption.encrypt(access_token) if access_token else None,
                refresh_token_enc=token_encryption.encrypt(refresh_token) if refresh_token else None,
                scope=scope,
                expires_at=expires_at,
                token_type=token_type,
            )
            session.add(conn)
        await session.commit()

        # Create session
        session_token, _ = await session_manager.create_session(str(user.id))
        response = RedirectResponse(url="/?auth=success", status_code=302)
        response.set_cookie(key="session", value=session_token, httponly=True, samesite="lax")
        return response
