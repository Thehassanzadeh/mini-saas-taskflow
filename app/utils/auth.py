"""
main file for authentication logic
"""

#####################################

import time
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException, status, Request, Depends

import jwt
from jwt.exceptions import (
    DecodeError,
    InvalidSignatureError,
    ExpiredSignatureError,
    InvalidTokenError,
    InvalidAudienceError,
    InvalidIssuerError,
    MissingRequiredClaimError,
)

from app.utils.password import verify_password as vp
from app.utils.hash_refresh_token import hash_refresh_token as ht
from app.db.engine import get_db
from app.config import settings as env
from app.db.models import UserModel, TeamUser, RefreshToken

from uuid import UUID

#####################################


async def get_user(db: AsyncSession, user_id: str):
    """
    simple function for get user from database if exist
    """

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def store_refresh_token(db: AsyncSession, token: str, user_id: UUID):
    """
    this function use for write refresh token in database
    """

    expires_at = datetime.now() + timedelta(minutes=env.REFRESH_TOKEN_EXPIRE_MINUTES)
    hashed_token = ht(token)
    new_token = RefreshToken(
        user_id=user_id, token=hashed_token, expires_at=expires_at, revoked=False
    )

    try:
        db.add(new_token)
        await db.commit()
    except Exception:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store refresh token",
        )


async def revoke_refresh_token(db: AsyncSession, token: str, user_id: UUID):
    """
    this function revoked refresh token in database
    """
    stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
    result = await db.execute(stmt)

    refresh = result.scalars().all()

    found = False
    hash_token = ht(token)
    for t in refresh:
        if (
            not t.revoked and t.expires_at > datetime.now(timezone.utc) and hash_token,
            t.token,
        ):
            t.revoked = True
            found = True
            break

    if found:
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to revoke refresh token",
            )


async def check_user(db: AsyncSession, identifier: str):
    """
    simple function for check user from database if exist
    """

    user_check = select(UserModel).where(
        or_(UserModel.email == identifier, UserModel.phone_number == identifier)
    )
    result = await db.execute(user_check)
    return result.scalar_one_or_none()


async def authenticated_user(db: AsyncSession, user_id: str, password: str):
    """
    this function use for get vp user
    """

    user = await get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user or password not found"
        )

    password_check = await vp(password, user.password_hash)
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
        decoded = jwt.decode(
            token,
            env.JWT_SECRET,
            algorithms=env.JWT_ALG,
            audience="mini-saas-api",
            issuer="mini-saas",
        )
        user_id = decoded.get("sub", None)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="authentication failed"
            )
        if time.time() > decoded["exp"]:
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


def decode_refresh_token(token: str):
    """
    decode refresh token logic here
    """
    try:
        payload = jwt.decode(
            token,
            env.JWT_SECRET,
            algorithms=[env.JWT_ALG],
            audience="mini-saas-api",
            issuer="mini-saas",
            options={"require": ["sub", "exp", "iat", "type", "iss", "aud"]},
        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token type"
            )

        return payload

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token expired",
        )

    except (
        InvalidAudienceError,
        InvalidIssuerError,
        MissingRequiredClaimError,
        InvalidTokenError,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid refresh token",
        )


async def get_user_refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """
    this function use for refreshing token by get access token from cookie
    """

    # get token from cookies
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="refresh token not found"
        )

    payload = decode_refresh_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id in token"
        )

    # UUID validation
    try:
        user_id = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid user id in token"
        )

    # database check for refresh token
    hash_token = ht(token)
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.token == hash_token,
        RefreshToken.revoked.is_(False),
    )
    result = await db.execute(stmt)
    stored_token = result.scalar_one_or_none()

    if stored_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="refresh token revoked or not recognized",
        )

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user not found",
        )

    return user


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
        "aud": "mini-saas-api",
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
        "aud": "mini-saas-api",
    }
    return jwt.encode(payload, env.JWT_SECRET, algorithm=env.JWT_ALG)
