
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

from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from app.utils.auth import get_authenticated_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import get_db
from app.services.teams import TeamOperation
from app.schema._input import CreateTeamInput

teams_router = APIRouter(prefix="/api/v1/teams")





@teams_router.post("/teams", status_code=status.HTTP_200_OK, tags=["teams"])
async def create_team(
    payload: CreateTeamInput,
    db: AsyncSession = Depends(get_db),
    user: str = Depends(get_authenticated_user)
):
    """
    this route create new team
    """
    team = await TeamOperation(db).create_team(user, payload)
    return team



@teams_router.get(
    "/teams/{team_id}", status_code=status.HTTP_200_OK, tags=["teams"]
)
async def user_teams(
    team_id: str, user: str = Depends(get_authenticated_user), db: AsyncSession = Depends(get_db)
):
    team = await TeamOperation(db).get_team_by_id(user, team_id)
    return team
    
    