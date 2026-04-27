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
from app.utils.auth import get_authenticated_user

from app.schema._output import UserInformationOutput

from app.schema._input import UpdateUserInput, UpdatePhoneInput

from app.services.users import UsersOperation

users_router = APIRouter(prefix="/api/v1/users")


@users_router.get("/me", status_code=status.HTTP_200_OK, tags={"users"})
async def get_current_user(
    user: str = Depends(get_authenticated_user),
) -> UserInformationOutput:
    """
    for read current user from access token
    """
    return user


@users_router.put("/me", status_code=status.HTTP_200_OK, tags=["users"])
async def update_user(
    payload: UpdateUserInput,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> UserInformationOutput:
    """
    this is for update user information by self
    """

    user = await UsersOperation(db).update_user_info(user, payload)
    return user


@users_router.post("/me/phone_number", status_code=status.HTTP_200_OK, tags=["users"])
async def get_new_phone_number(
    phone_number: str,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_authenticated_user),
):
    try:
        send_otp = await UsersOperation(db).send_register_sms_phone_update(
            phone_number, user
        )
        if send_otp:
            return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
        )


@users_router.put("/me/phone_number", status_code=status.HTTP_200_OK, tags=["users"])
async def update_user_phone_number(
    payload: UpdatePhoneInput,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> UserInformationOutput:
    """
    use for update user phone number
    """
    update = await UsersOperation(db).update_user_phone_number(user, payload)
    return update


@users_router.delete("/me", status_code=status.HTTP_200_OK, tags=["users"])
async def delete_user(
    user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    user_delete = await UsersOperation(db).delete_user(user)
    return user_delete


@users_router.get("me/teams", status_code=status.HTTP_200_OK, tags=["users"])
async def user_teams(
    user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    teams = await UsersOperation(db).user_teams(user)
    return teams


@users_router.get("me/projects", status_code=status.HTTP_200_OK, tags=["users"])
async def user_projects(
    user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    projects = await UsersOperation(db).user_projects(user)
    return projects


@users_router.get("me/tasks", status_code=status.HTTP_200_OK, tags=["users"])
async def user_tasks(
    user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    tasks = await UsersOperation(db).user_projects(user)
    return tasks
