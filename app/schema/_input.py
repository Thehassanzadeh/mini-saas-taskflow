from pydantic import BaseModel, Field, EmailStr, field_serializer

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
        title="Phone Number", description="input your phone number"
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

    @field_serializer("fist_name")
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
