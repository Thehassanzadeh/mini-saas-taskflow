from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.db.models import (
    ProjectUser,
    ProjectModel,
    UserModel,
    TeamModel,
    TeamUser,
    RoleModel
)



class ProjectOperation:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def create_project(self, user: str, team_id: UUID, payload: str):
        """
        Create project

        Args:
        User: user which must be allowed
        Team_id: the id of the team
        Payload: project info

        Return:
        New project information
        """
        allow_stmt = (
            select(TeamUser)
            .where(
                TeamUser.user_id == user.id,
                TeamUser.team_id == team_id
            )
            .options(selectinload(TeamUser.role))
        )
        allow_result = await self.db.execute(allow_stmt)
        allow_user = allow_result.scalar_one_or_none()
        print(allow_user)

        if allow_user.role.name not in ("team-owner", "team-manager"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="your not allow to do this",
            )
        
        role = await self.db.scalar(
            select(RoleModel).where(RoleModel.name == "project-owner")
        )

        try:
            new_project = ProjectModel(
                name = payload.name,
                team_id = team_id,
                description = payload.description,
                goal = payload.goal,
                ttl = payload.ttl
            )
        
            self.db.add(new_project)
            await self.db.commit()
            await self.db.refresh(new_project)

            project_user = ProjectUser(
                user_id = user.id,
                project_id = new_project.id,
                team_id = team_id,
                role_id = role.id
            )

            self.db.add(project_user)
            await self.db.commit()

            return new_project
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail= {"error": str(e)}
            )
        
            
        
