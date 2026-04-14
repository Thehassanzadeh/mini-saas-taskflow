"""
✅ Authentication
POST /auth/register # signup (create user)
POST /auth/login # login → access + refresh token
POST /auth/logout # logout (invalidate refresh token)
POST /auth/refresh # refresh access token

✅ Password Management
POST /auth/password/forgot # request reset password (email)
POST /auth/password/reset # reset password (token)
PUT /auth/password/change # change password (logged-in user)

✅ Email / Account Verification (اختیاری ولی حرفه‌ای)
POST /auth/email/verify # verify email with token
POST /auth/email/resend # resend verification email

✅ Session / Token Info
GET /auth/me # current auth info (id, roles, scopes)

✅ Optional (Advanced – Later)
OAuth (بدون شکستن API)
GET /auth/oauth/{provider} # google, github, …
GET /auth/oauth/{provider}/callback
Token Management
GET /auth/sessions
DELETE /auth/sessions/{session_id}
"""

##############################################

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException, Response, Request, Cookie
from fastapi.security import HTTPBearer

from sqlalchemy import select

from app.db.models import UserModel

from app.schema._input import CreateUserInput, LoginInput

from app.schema._output import LoginOutput

from app.db.engine import get_db
from app.utils.password import hash_password as hash, verify_password as vp

from app.utils.auth import (
    check_user,
    create_access_token,
    create_refresh_token,
    store_refresh_token,
    revoke_refresh_token,
    decode_refresh_token,
)

##############################################


auth_router = APIRouter(prefix="/api/v1/auth")
security = HTTPBearer()


COOKIE_KWARGS = {
    "path": "/",
    "httponly": True,
    "secure": True,
    "samesite": "lax",
}


###############################################


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, tags=["auth"])
async def create_user(
    response: Response, payload: CreateUserInput, db: AsyncSession = Depends(get_db)
):
    """
    thsi route usr for register user and create database new record
    """

    new_user = UserModel(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        phone_number=payload.phone_number,
        password_hash=hash(payload.password),
    )

    # check user exist
    identifier = payload.email or payload.phone_number
    user = await check_user(db, identifier)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email or phone number exist"
        )

    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        access_token = create_access_token(subject=str(new_user.id))
        refresh_token = create_refresh_token(subject=str(new_user.id))

        response.set_cookie(key="access_token", value=access_token, **COOKIE_KWARGS)
        response.set_cookie(key="refresh_token", value=refresh_token, **COOKIE_KWARGS)

        await store_refresh_token(db, refresh_token, new_user.id)

        return "your register successfully"

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"register was failed, error:{e}",
        )


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=LoginOutput, tags=["auth"]
)
async def login_user(
    response: Response, payload: LoginInput, db: AsyncSession = Depends(get_db)
):
    """
    this route use for login user by email or phone number whit password
    """

    identifier = payload.phone_number or payload.email
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="phone number or email must be input",
        )

    user = await check_user(db, identifier)

    if not user or not vp(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid input, user info or password is wrong",
        )

    # create token
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))

    # set cookies
    response.set_cookie(key="access_token", value=access_token, **COOKIE_KWARGS)
    response.set_cookie(key="refresh_token", value=refresh_token, **COOKIE_KWARGS)

    # store refresh token
    await store_refresh_token(db, refresh_token, user.id)

    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
        },
    }


@auth_router.post("/logout", status_code=status.HTTP_200_OK, tags=["auth"])
async def logout_user(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    """
    this route logout user by delete cookies and invalidate refresh token
    """

    payload = decode_refresh_token(request.cookies.get("refresh_token"))
    user_id = payload.get("sub")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    if refresh_token:
        await revoke_refresh_token(db, refresh_token, user_id)

    return {"message": "logout successfully"}
