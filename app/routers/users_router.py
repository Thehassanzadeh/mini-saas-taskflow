"""
🔵 1. USER (Self / Profile)

POST /users # create user (signup)

GET /users/me # get current user

PUT /users/me # update current user

DELETE /users/me # delete current user

GET /users/me/teams # list user teams

GET /users/me/projects # list user projects (optional)

GET /users/me/tasks # list tasks assigned to user

"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.schema._input import CreateUserInput
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db
from app.utils.auth import (
    get_authenticated_user
)
from app.schema._output import (
    UserInformationOutput
)

from app.schema._input import (
    UpdateUserInput
)

from app.services.users import (
    UsersOperation
)
users_router = APIRouter(prefix="/api/v1/users")






@users_router.get("/me", status_code=status.HTTP_200_OK, tags={"users"})
async def get_current_user(user: str = Depends(get_authenticated_user)
) -> UserInformationOutput:
    """
    for read current user from access token
    """
    return user



@users_router.put(
    "/me",status_code=status.HTTP_200_OK, tags=["users"]
)
async def update_user(
    payload: UpdateUserInput, user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
) -> UserInformationOutput:
    """
    this is for update user information by self
    """

    user = await UsersOperation(db).update_user_info(user, payload)
    return user

    

@users_router.put(
    "/me/{phone_number}", status_code=status.HTTP_200_OK, tags=["users"]
)
async def update_user_phone_number():
    """
    use for update user phone number
    """


# @users_router.delete("me")


# @users_router.get("me/teams")


# @users_router.get("me/projects")


# @users_router.get("me/tasks")

