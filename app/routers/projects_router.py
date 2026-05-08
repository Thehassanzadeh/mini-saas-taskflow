"""
🟡 3. PROJECT

POST /projects

GET /projects/{project_id}

PUT /projects/{project_id}

DELETE /projects/{project_id}

Project Tasks
GET /projects/{project_id}/tasks
"""


from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from app.utils.auth import (
    get_authenticated_user
)

from app.db.engine import get_db

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema._input import (
    CreateProjectInput
)

from app.services.projects import ProjectOperation


projects_router = APIRouter(prefix="/api/v1/projects")


@projects_router.post("", status_code=status.HTTP_200_OK, tags=["projects"])
async def create_project(
    payload: CreateProjectInput,
    team_id : str,
    user: str = Depends(get_authenticated_user),
    db: AsyncSession = Depends(get_db)
):
    project = await ProjectOperation(db).create_project(user, team_id, payload)