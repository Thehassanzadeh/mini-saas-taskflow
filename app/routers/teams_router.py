"""
🟢 2. TEAM

POST /teams # create team

GET /teams/{team_id} # view team

PUT /teams/{team_id} # update team

DELETE /teams/{team_id} # delete team

Members
GET /teams/{team_id}/users # list team members

POST /teams/{team_id}/users # add user to team

# PUT /teams/{team_id}/users/{user_id} # update role in team

DELETE /teams/{team_id}/users/{user_id} # remove user from team

Team Projects
GET /teams/{team_id}/projects

Team Tasks
GET /teams/{team_id}/tasks
"""

from fastapi import APIRouter, HTTPException, status, Depends

from app.utils.auth import get_authenticated_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db
from app.services.teams import TeamOperation
from app.schema._input import CreateTeamInput, AddUserToTeamInput
from typing import List
from app.schema._output import SimpleUserInfoOutput

teams_router = APIRouter(prefix="/api/v1/teams")


@teams_router.post("", status_code=status.HTTP_200_OK, tags=["teams"])
async def create_team(
    payload: CreateTeamInput,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_authenticated_user),
):
    """
    this route create new team
    """
    team = await TeamOperation(db).create_team(user, payload)
    return team


@teams_router.get("/{team_id}", status_code=status.HTTP_200_OK, tags=["teams"])
async def get_team_by_id(
    team_id: str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamOperation(db).get_team_by_id(user, team_id)
    return team


@teams_router.put("/{team_id}", status_code=status.HTTP_200_OK, tags=["teams"])
async def update_team(
    team_id: str,
    payload: CreateTeamInput,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    team = await TeamOperation(db).update_team(user, payload, team_id)
    return team


@teams_router.delete("/{team_id}", status_code=status.HTTP_200_OK, tags=["teams"])
async def delete_team(
    team_id: str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    delete = await TeamOperation(db).delete_team(user, team_id)
    return delete


@teams_router.get("/{team_id}/users", status_code=status.HTTP_200_OK, tags=["teams"])
async def get_teams_users(
    team_id: str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
) -> List[SimpleUserInfoOutput]:
    users = await TeamOperation(db).return_all_users(user, team_id)
    return users


@teams_router.post("/{team_id}/users", status_code=status.HTTP_200_OK, tags=["teams"])
async def add_user_to_team(
    team_id: str,
    payload: AddUserToTeamInput,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):
    add_user = await TeamOperation(db).add_user_to_team(user, team_id, payload)
    return add_user


@teams_router.post(
    "/{team_id}/users/{user_id}", status_code=status.HTTP_200_OK, tags=["teams"]
)
async def update_user_role(
    team_id: str,
    user_id: str,
    new_role: str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):

    role = await TeamOperation(db).update_user_role(user, team_id, user_id, new_role)
    return role


@teams_router.delete(
    "/{team_id}/users/{user_id}", status_code=status.HTTP_200_OK, tags=["teams"]
)
async def delete_user_form_team(
    team_id: str,
    user_id: str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db),
):

    delete = await TeamOperation(db).delete_user(user, team_id, user_id)
    return delete
