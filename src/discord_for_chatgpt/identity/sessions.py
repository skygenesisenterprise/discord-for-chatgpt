import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select

from ..config import settings
from ..db.models import Session, User
from ..db.session import AsyncSessionLocal


class SessionManager:
    @staticmethod
    def _hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    async def create_session(user_id: str, expires_in_hours: int = 24) -> tuple[str, Session]:
        token = secrets.token_urlsafe(48)
        token_hash = SessionManager._hash_token(token)
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        async with AsyncSessionLocal() as session:
            db_session = Session(
                user_id=user_id,
                session_token_hash=token_hash,
                expires_at=expires_at,
            )
            session.add(db_session)
            await session.commit()
            await session.refresh(db_session)
            return token, db_session

    @staticmethod
    async def validate_session(token: str) -> Optional[User]:
        if not token:
            return None
        token_hash = SessionManager._hash_token(token)
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Session).where(Session.session_token_hash == token_hash, Session.revoked_at.is_(None))
            )
            db_session = result.scalar_one_or_none()
            if not db_session:
                return None
            if db_session.expires_at < datetime.utcnow():
                return None
            result = await session.execute(select(User).where(User.id == db_session.user_id))
            return result.scalar_one_or_none()


session_manager = SessionManager()
