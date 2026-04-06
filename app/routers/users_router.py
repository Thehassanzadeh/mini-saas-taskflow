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

from fastapi import APIRouter, HTTPException





users_router = APIRouter(prefix="/api/v1")





@users_router.post("/users")


@users_router.get("/users/me")


@users_router.put("/users/me")


@users_router.delete("/users/me")


@users_router.get("/users/me/teams")


@users_router.get("/users/me/projects")


@users_router.get("/users/me/tasks")

