from pydantic import (
    BaseModel,
    Field,
    EmailStr,
    field_serializer,
    model_validator,
    field_validator,
)
from typing import Optional
import re


class CreateUserInput(BaseModel):
    """
    for user input in /users route to create user
    """

    first_name: str = Field(title="First Name", description="input your first name")

    last_name: str = Field(title="Last Name", description="input your last name")

    email: EmailStr = Field(
        title="Email", description="input your email, must be valid"
    )

    phone_number: str = Field(
        title="Phone Number",
        description="input your mobile number",
        pattern=r"^09\d{9}$",
    )

    password: str = Field(
        title="password",
        description="input your password, must be 8 character or more",
        min_length=8,
        max_length=64,
    )
    password_confirm: str = Field(
        title="password confirm",
        description="input your password again",
        min_length=8,
        max_length=64,
    )

    @model_validator(mode="after")
    def password_match(self):
        """
        this function use for confirm password
        """

        if self.password != self.password_confirm:
            raise ValueError("your password dose not match")
        return self

    @field_serializer("first_name")
    def first_name_serializer(self, value):
        """
        use for make first name capital
        """
        return value.capitalize()

    @field_serializer("last_name")
    def last_name_serializer(self, value):
        """
        use for make last name capital
        """
        return value.capitalize()


class LoginInput(BaseModel):
    """
    this class use for login data which user input like email, phone number and password
    """

    email: Optional[EmailStr] = Field(
        default=None, title="Email", description="input your email"
    )

    phone_number: Optional[str] = Field(
        title="Phone Number",
        description="input your mobile number",
        pattern=r"^09\d{9}$",
    )

    password: str = Field(
        title="Password",
        description="input your password",
        min_length=8,
        max_length=64,
    )

    @field_validator("email", "phone_number", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_email_or_phone(self):
        if not self.email and not self.phone_number:
            raise ValueError("Either email or phone number must be provided")
        if self.email and self.phone_number:
            raise ValueError("Provide only one of email or phone number")
        return self


class OtpVerifyInput(BaseModel):
    """
    user input get otp code from user
    """

    code: int
