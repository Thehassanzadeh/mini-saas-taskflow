"""
this code hash refresh token for store in db
"""

import  hashlib

def hash_refresh_token(token: str) -> str:
    """
    this function hash refresh token to store in db
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


# def verify_token(token: str, hashed: str) -> bool:
#     """
#     compare token with hashed one and if it right return True
#     """
#     return pwd_context.verify(token, hashed)
