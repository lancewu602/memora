import hmac
import hashlib
from datetime import datetime, timedelta
import secrets

from ..config import TOKEN_SECRET, TOKEN_EXPIRE_HOURS


def generate_token(api_key: str) -> str:
    expire_at = datetime.now() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    expire_ts = str(int(expire_at.timestamp()))
    random_part = secrets.token_urlsafe(32).replace("-", "").replace("_", "")
    message = f"{random_part}:{expire_ts}"
    signature = hmac.new(TOKEN_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
    token = f"{random_part}.{expire_ts}.{signature}"
    return token


def verify_token(token: str) -> bool:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return False
        random_part, expire_ts, signature = parts
        expire_at = datetime.fromtimestamp(int(expire_ts))
        if datetime.now() > expire_at:
            return False
        message = f"{random_part}:{expire_ts}"
        expected_signature = hmac.new(TOKEN_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    except Exception:
        return False
