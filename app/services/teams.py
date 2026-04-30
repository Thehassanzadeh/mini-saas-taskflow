from fastapi import HTTPException, status

from app.db.models import UserModel, TeamModel, TeamUser, RoleModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from uuid import UUID

import sqlalchemy as sa


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

        role = await self.db.scalar(
            select(RoleModel).where(RoleModel.name == "team-owner")
        )

        try:
            self.db.add(team)
            await self.db.commit()
            await self.db.refresh(team)

            team_user = TeamUser(user_id=user.id, team_id=team.id, role_id=role.id)

            self.db.add(team_user)
            await self.db.commit()

            return team
        except Exception as e:
            await self.db.rollback()
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
            raise HTTPException(status_code=status.HTTP_200_OK, detail="team not found")
        return team

    async def update_team(self, user: str, payload: str, team_id: UUID):
        """
        Update team info by owner

        Args:
        User: user which must be team owner
        Payload: new info(name or description)
        Team_id: the id of the team

        Return:
        New team information
        """
        stmt = select(TeamModel).where(
            TeamModel.id == team_id, TeamModel.owner_id == user.id
        )
        result = await self.db.execute(stmt)
        team = result.scalar_one_or_none()
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team not found, or user not allow to cheng",
            )
        if payload.name:
            team.name = payload.name
        if payload.description:
            team.description = payload.description

        try:
            await self.db.commit()
            await self.db.refresh(team)

            return team
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def delete_team(self, user: str, team_id: UUID):
        """
        Delete team  by owner

        Args:
        User: user which must be team owner
        Team_id: the id of the team

        Return:
        some message means successfully
        """
        stmt = select(TeamModel).where(
            TeamModel.id == team_id, TeamModel.owner_id == user.id
        )
        result = await self.db.execute(stmt)
        team = result.scalar_one_or_none()
        if team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="team not found, or user not allow to cheng",
            )
        team_user_stmt = select(TeamUser).where(TeamUser.team_id == team.id)
        team_user_result = await self.db.execute(team_user_stmt)
        team_user = team_user_result.scalars().all()

        try:
            await self.db.delete(team)
            for team in team_user:
                await self.db.delete(team)
            await self.db.commit()

            return {"message": "team successfully delete"}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def return_all_users(self, user: str, team_id: UUID):
        """
        Return all user in team

        Args:
        User: user info
        Team_id: the id of the team

        Return:
        A list of all user in team
        """
        is_member_stmt = select(
            sa.exists().where(TeamUser.team_id == team_id, TeamUser.user_id == user.id)
        )

        is_member = await self.db.scalars(is_member_stmt)

        if not is_member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="you are not a member of this team",
            )

        users_stmt = (
            select(UserModel)
            .join(TeamUser, TeamUser.user_id == UserModel.id)
            .where(TeamUser.team_id == team_id)
        )
        result = await self.db.execute(users_stmt)
        return list(result.scalars().all())

    async def add_user_to_team(self, user: str, team_id: UUID, payload: str):
        """
        Add user to team by allowed users

        Args:
        User: user which must be allowed
        Payload: new user info(id  and role)
        Team_id: the id of the team

        Return:
        message or a list of the teams users
        """

        allow_stmt = (
            select(TeamUser)
            .where(
                TeamUser.user_id == user.id,
                TeamUser.team_id == team_id,
            )
            .options(selectinload(TeamUser.role))
        )
        allow_result = await self.db.execute(allow_stmt)
        allow_user = allow_result.scalar_one_or_none()
        print(allow_user)

        if allow_user.role.name != "team-owner":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="your not allow to do this",
            )

        if payload.role == "team-user":
            role = "be98264e-a10a-43ac-ad38-5988eb305316"

        try:
            new_user = TeamUser(team_id=team_id, user_id=payload.user_id, role_id=role)

            self.db.add(new_user)
            await self.db.commit()

            return {"message": "user successfully add to team"}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def update_user_role(
        self, user: str, team_id: UUID, user_id: UUID, new_role: str
    ):
        """
        Update user role in team

        Args:
        User: user which must be allowed
        User_id: the user id which change role
        Team_id: the id of the team
        New_role: new role

        Return:
        the user new info
        """

        allow_stmt = (
            select(TeamUser)
            .where(
                TeamUser.user_id == user.id,
                TeamUser.team_id == team_id,
            )
            .options(selectinload(TeamUser.role))
        )
        allow_result = await self.db.execute(allow_stmt)
        allow_user = allow_result.scalar_one_or_none()
        print(allow_user)

        if allow_user.role.name != "team-owner":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="your not allow to do this",
            )

        role_stmt = select(RoleModel).where(RoleModel.name == new_role)
        role_result = await self.db.execute(role_stmt)
        role = role_result.scalar_one_or_none()
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="role not found"
            )

        user_role_stmt = select(TeamUser).where(
            TeamUser.team_id == team_id, TeamUser.user_id == user_id
        )
        user_role_result = await self.db.execute(user_role_stmt)
        user_role = user_role_result.scalar_one_or_none()
        if user_role is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user not found in this team",
            )

        try:
            user_role.role_id = role.id
            await self.db.commit()
            await self.db.refresh(user_role)
            return user_role
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def delete_user(self, user: str, team_id: UUID, user_id: UUID):
        """
        Delete user from team

        Args:
        User: user which must be allowed
        User_id: the user id which change role
        Team_id: the id of the team

        Return:
        some message for successfully report
        """

        allow_stmt = (
            select(TeamUser)
            .where(
                TeamUser.user_id == user.id,
                TeamUser.team_id == team_id,
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

        user_team_stmt = select(TeamUser).where(
            TeamUser.team_id == team_id, TeamUser.user_id == user_id
        )
        user_team_result = await self.db.execute(user_team_stmt)
        user_team = user_team_result.scalar_one_or_none()

        if user_team is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="user not in this team"
            )

        try:
            await self.db.delete(user_team)
            await self.db.commit()
            return {"message": "User deleted from team successfully"}
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )
