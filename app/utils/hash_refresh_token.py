"""
this code hash refresh token for store in db
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_refresh_token(token: str) -> str:
    """
    this function hash refresh token to store in db
    """
    return pwd_context.hash(token)


def verify_token(token: str, hashed: str) -> bool:
    """
    compare token with hashed one and if it right return True
    """
    return pwd_context.verify(token, hashed)
