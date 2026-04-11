from pydantic import BaseModel
from uuid import UUID


class UserPublic(BaseModel):
    """
    a mother model for user
    """

    id: UUID
    email: str


class LoginOutput(BaseModel):
    """
    use for login output message and info
    """

    message: str
    user: UserPublic
