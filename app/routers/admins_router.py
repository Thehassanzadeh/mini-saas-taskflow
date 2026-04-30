from fastapi import APIRouter, HTTPException, status, Depends

from app.utils.auth import get_authenticated_admin

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema._input import CreateRoleInput

from app.db.engine import get_db

from app.services.admins import AdminOperation

admin_router = APIRouter(prefix="/api/v1/admin")


@admin_router.post("/role", status_code=status.HTTP_200_OK, tags=["admin"])
async def create_role(
    payload: CreateRoleInput,
    user: str = Depends(get_authenticated_admin),
    db: AsyncSession = Depends(get_db),
):
    new_role = await AdminOperation(db).create_role(payload, user)
    return new_role
