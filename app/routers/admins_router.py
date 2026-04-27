from fastapi import (
    APIRouter,
    HTTPException,
    status,
    Depends
)

from app.utils.auth import get_authenticated_admin

from sqlalchemy.ext.asyncio import AsyncSession

from app.schema._input import CreateRoleInpout

from app.db.engine import get_db
admin_router = APIRouter(prefix="/api/v1/admin")


@admin_router.post("/role", status_code=status.HTTP_200_OK, tags=["admin"])
def create_role(
    pyload: CreateRoleInpout,
    user: str = Depends(get_authenticated_admin),
    db: AsyncSession = Depends(get_db),
):
    