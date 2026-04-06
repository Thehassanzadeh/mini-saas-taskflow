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



from fastapi import APIRouter, status, Depends
from app.schema._input import CreateUserInput
from app.db.engine import get_db
from sqlalchemy.ext.asyncio import AsyncSession

auth_router = APIRouter(prefix="/api/v1")


@auth_router.post(
    "/auth/register",
    status_code=status.HTTP_201_CREATED,
    tags=["users"]
)
async def create_user(
    payload: CreateUserInput,
    db: AsyncSession = Depends(get_db)
) -> str:
    """
    thsi route usr for register user and create database new record
    """
    
    
