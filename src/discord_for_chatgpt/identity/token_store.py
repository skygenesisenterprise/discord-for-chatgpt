import base64
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken

from ..config import settings


class TokenEncryption:
    def __init__(self) -> None:
        key = settings.encryption_key
        if not key:
            # In dev, generate a key if missing - but in production we must fail
            # For safety, generate deterministic key from secret_key
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"discord-for-chatgpt",
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode())).decode()
        try:
            self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except Exception:
            # Fallback
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"discord-for-chatgpt",
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(settings.secret_key.encode())).decode()
            self.fernet = Fernet(key.encode())

    def encrypt(self, value: str) -> str:
        if not value:
            return ""
        return self.fernet.encrypt(value.encode()).decode()

    def decrypt(self, value: str) -> Optional[str]:
        if not value:
            return None
        try:
            return self.fernet.decrypt(value.encode()).decode()
        except InvalidToken:
            return None


token_encryption = TokenEncryption()
