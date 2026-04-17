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

from fastapi import APIRouter, HTTPException, status, Depends, 
from app.schema._auth_input import CreateUserInput
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db



users_router = APIRouter(prefix="/api/v1")





@users_router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    tags=["users"]
)
async def create_user(
    payload: CreateUserInput,
    db: AsyncSession = Depends(get_db)
) -> str


@users_router.get("/users/me")


@users_router.put("/users/me")


@users_router.delete("/users/me")


@users_router.get("/users/me/teams")


@users_router.get("/users/me/projects")


@users_router.get("/users/me/tasks")

