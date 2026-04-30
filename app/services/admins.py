from fastapi import HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RoleModel


class AdminOperation:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_role(self, payload: str, user: str):
        """
        Admin create role

        Args:
        Payload: the role info which input admin
        user: admin info

        Return:
        the new role info
        """
        new_role = RoleModel(
            name=payload.name, description=payload.description, owner_id=user.id
        )

        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="input cat not be empty"
            )
        try:
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role)

            return new_role
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )
