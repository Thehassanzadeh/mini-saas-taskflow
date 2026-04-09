"""
main file for authentication logic
"""

import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Request, Depends

import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError

from app.utils.password import verify_password as verify
from app.db.engine import get_db
from app.config import settings as env
from app.db.models import UserModel, TeamUser


async def get_user(db: AsyncSession, user_id: str):
    """
    simple function for get user from database if exist
    """

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def check_user(db: AsyncSession, phone_number: str, email: str):
    """
    simple function for check user from database if exist
    """

    phone_check = select(UserModel).where(UserModel.phone_number == phone_number)
    email_check = select(UserModel).where(UserModel.email == email)
    phone_result = await db.execute(phone_check)
    email_result = await db.execute(email_check)
    if (phone_result is None) and (email_result is None):
        return True


async def authenticated_user(db: AsyncSession, user_id: str, password: str):
    """
    this function use for get verify user
    """

    user = await get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user or password not found"
        )

    password_check = await verify(password, user.password_hash)
    if not password_check:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user or password not found"
        )

    return user


async def get_authenticated_user(request: Request, db: AsyncSession = Depends(get_db)):
    """
    this function use for get token from cookie and
    decoded it for get user information and authenticated user
    """

    token = request.cookies.get("access_token")

    try:
        decoded = jwt.decode(token, env.JWT_SECRET, algorithms=env.JWT_ALG)
        user_id = decoded.get("user_id", None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication failed"
            )
        if time.time() > datetime.fromtimestamp(decoded.get("exp")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication failed"
            )
        if decoded.get("type") == "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication failed"
            )
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    except InvalidSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token"
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="decoded token failed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"authentication has failed, error: {e}",
        )


async def get_authenticated_admin(
    user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    """
    this function use for authenticated admin
    """
    user_id = user.id
    stmt = select(TeamUser).where(TeamUser.user_id == user_id)
    result = await db.execute(stmt)
    user_obj = result.scalar_one_or_none()
    if not user_obj.role_id == 2:  # 2 is id for admin
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you are not allowed to get this",
        )
    return user_obj


def create_access_token(
    *, subject: str, expires_minutes: int = env.ACCESS_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    this function use for create a access token for user
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "iss": "mini-saas",
        "aud": "mini-saas-api"
    }
    return jwt.encode(payload, env.JWT_SECRET, algorithm=env.JWT_ALG)


def create_refresh_token(
    *, subject: str, expires_minutes: int = env.REFRESH_TOKEN_EXPIRE_MINUTES
) -> str:
    """
    this function use for create a refresh token for user
    """

    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
        "iss": "mini-saas",
        "aud": "mini-saas-api"
    }
    return jwt.encode(payload, env.JWT_SECRET, algorithm=env.JWT_ALG)
