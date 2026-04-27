from fastapi import HTTPException, status

from app.db.models import (
    UserModel,
    TeamModel,
    TeamUser
)

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from uuid import UUID

class TeamOperation:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_team(self, user: str, payload: str):
        """
        Create team record with payload and user information input

        Args:
        User: user information
        Payload: team information

        Return:
        new team record information
        """
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="input can not empty"
            )
        team = TeamModel(
            owner_id=user.id, name=payload.name, description=payload.description
        )
        team_user = TeamUser(
            
        )

        try:
            self.db.add(team)
            await self.db.commit()
            await self.db.refresh(team)

            return team
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def get_team_by_id(self, user: str, team_id: UUID):
        """
        show the team which user want
        
        Args:
        User: user information
        Team_id: id of the team which user input
        
        Return:
        the information of the team
        """

        stmt = (
            select(TeamModel)
            .join(TeamUser)
            .where(
                TeamUser.team_id == team_id,
                TeamUser.user_id == user.id,
            )
        )
        result = await self.db.execute(stmt)
        team = result.scalar_one_or_none()
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail="team not found"
            )
        return team

