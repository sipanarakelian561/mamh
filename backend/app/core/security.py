from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(
    subject: str,
    role: str,
    is_admin: bool,
    must_change_password: bool = False,
    school_id: int | None = None,
    expires_minutes: int | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "role": role,
        "adm": bool(is_admin),
        "pwd": bool(must_change_password),
        "sch": school_id,
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError("Invalid token") from e

    if not isinstance(payload, dict):
        raise ValueError("Invalid token payload")

    if not payload.get("sub"):
        raise ValueError("Invalid token subject")

    role = payload.get("role")
    if role not in {"student", "teacher", "admin", "super_admin"}:
        raise ValueError("Invalid token role")

    if "adm" in payload and not isinstance(payload["adm"], bool):
        raise ValueError("Invalid admin claim")
    if "pwd" in payload and not isinstance(payload["pwd"], bool):
        raise ValueError("Invalid password-change claim")
    if "sch" in payload and payload["sch"] is not None and not isinstance(payload["sch"], int):
        raise ValueError("Invalid school claim")

    return payload
