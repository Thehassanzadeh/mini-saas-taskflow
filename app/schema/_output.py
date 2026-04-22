from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


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


class SmsVerificationOutput(BaseModel):
    phone_number: str
    prompt: str


class SmsVerificationCompleteOutput(BaseModel):
    phone_number: str
    prompt: str

class UserInformationOutput(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone_number:str
    is_verified: bool
    created_at: datetime




