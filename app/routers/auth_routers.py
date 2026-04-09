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


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, status, Depends, HTTPException, Response, Request
from fastapi.security import

from app.db.models import UserModel
from app.schema._input import CreateUserInput
from app.db.engine import get_db


from app.utils.password import hash_password as hash

from app.utils.auth import check_user, create_access_token, create_refresh_token

auth_router = APIRouter(prefix="/api/v1")


COOKIE_KWARGS = {
    "path": "/",
    "httponly": True,
}



@auth_router.post("/auth/register", status_code=status.HTTP_201_CREATED, tags=["auth"])
async def create_user(
    response: Response, payload: CreateUserInput, db: AsyncSession = Depends(get_db)
) -> str:
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

    user = await check_user(db, payload.phone_number, payload.email)
    if  user == False:
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

        return "your register successfully"
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"register was failed, error:{e}"
        )


@auth_router.post("/auth/login", status_code=status.HTTP_200_OK, tags=["auth"])
def login_user(
    request: Request, response: Response, 
)