from fastapi import (
    HTTPException,
    status
)

from sqlalchemy.ext.asyncio import AsyncSession



class AdminOperation:
    def __int__(self, db: AsyncSession):
        self.db = db

    async def create_role(
            payload
    )