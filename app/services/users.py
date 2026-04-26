import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.smsir import hash_otp_code as hoc, generate_code, send_otp_sms

from fastapi import HTTPException, status, Response
from uuid import UUID

from app.schema._output import SmsVerificationOutput, SmsVerificationCompleteOutput

from sqlalchemy import select

from app.schema._input import UpdateUserInput, UpdatePhoneInput

from app.db.models import (
    OTP,
    UserModel,
    TeamUser,
    TeamModel,
    ProjectModel,
    TaskModel,
    UserTask,
    ProjectUser,
    
)

from app.config import settings as env
from app.utils.auth import (
    create_access_token,
    create_refresh_token,
    store_refresh_token,
)

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


COOKIE_KWARGS = {
    "path": "/",
    "httponly": True,
    "secure": True,
    "samesite": "lax",
}

# def send_sms(phone_number: str, code: str) -> None:
#     try:
#         send_otp_sms(phone_number, code)
#     except Exception:
#         logger.warning("SMS Provider failed, printing code for %s", phone_number)
#         logger.info("SMS to %s: your verification code is %s", phone_number, code)


class UsersOperation:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_register_verification_sms(
        self, phone_number: str, channel: str = "sms", purpose: str = "OTP"
    ) -> SmsVerificationOutput:

        now = datetime.now()
        stmt = select(UserModel).where(UserModel.phone_number == phone_number)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="user or phone number not found",
            )

        otp_stmt = select(OTP).where(
            OTP.target == phone_number,
            OTP.channel == channel,
            OTP.purpose == purpose,
            OTP.expires_at > now,
            OTP.is_used.is_(False),
        )
        otp_result = await self.db.execute(otp_stmt)
        otp = otp_result.scalar_one_or_none()
        if otp:
            otp.is_used = True
            self.db.commit()

        code = generate_code()
        code_hash = hoc(code)
        expires_at = datetime.now() + timedelta(minutes=env.OTP_EXPIRE_MINUTES)
        new_otp = OTP(
            user_id=user.id,
            channel=channel,
            target=phone_number,
            purpose=purpose,
            code_hash=code_hash,
            expires_at=expires_at,
            last_sent_at=now,
        )
        self.db.add(new_otp)
        await self.db.commit()

        send_message = send_otp_sms(phone_number, code)
        print(send_message)

        return SmsVerificationOutput(
            phone_number=phone_number, prompt="verification code sent"
        )

    async def complete_otp(
        self, code: str, phone_number: str, response: Response, purpose: str = "OTP"
    ) -> SmsVerificationCompleteOutput:

        hash_code = hoc(code)
        now = datetime.now()
        stmt = select(OTP).where(
            OTP.target == phone_number,
            OTP.code_hash == hash_code,
            OTP.purpose == purpose,
            OTP.is_used.is_(False),
            OTP.expires_at > now,
        )
        result = await self.db.execute(stmt)
        otp_obj = result.scalar_one_or_none()

        try:
            if not otp_obj:
                raise ValueError("your otp is wrong")
            stmt = select(UserModel).where(UserModel.phone_number == phone_number)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            user.is_verified = True
            otp_obj.is_used = True
            otp_obj.used_at = now
            await self.db.commit()

            if response:
                # create token
                access_token = create_access_token(subject=str(user.id))
                refresh_token = create_refresh_token(subject=str(user.id))

                # set cookies
                response.set_cookie(
                    key="access_token", value=access_token, **COOKIE_KWARGS
                )
                response.set_cookie(
                    key="refresh_token", value=refresh_token, **COOKIE_KWARGS
                )

                # store refresh token
                await store_refresh_token(self.db, refresh_token, user.id)

            print("successfully")
            return SmsVerificationCompleteOutput(
                phone_number=phone_number, prompt="verify successfully"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def complete_otp_phone_update(
        self, code: str, phone_number: str, purpose: str = "OTP"
    ) -> SmsVerificationCompleteOutput:

        hash_code = hoc(code)
        now = datetime.now()
        stmt = select(OTP).where(
            OTP.target == phone_number,
            OTP.code_hash == hash_code,
            OTP.purpose == purpose,
            OTP.is_used.is_(False),
            OTP.expires_at > now,
        )
        result = await self.db.execute(stmt)
        otp_obj = result.scalar_one_or_none()

        try:
            if not otp_obj:
                raise ValueError("your otp is wrong")
            stmt = select(UserModel).where(UserModel.phone_number == phone_number)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            user.is_verified = True
            otp_obj.is_used = True
            otp_obj.used_at = now
            await self.db.commit()

            print("successfully")
            return SmsVerificationCompleteOutput(
                phone_number=phone_number, prompt="verify successfully"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def update_user_info(self, user: str, payload: UpdateUserInput):
        """
        Update user information with provided field only

        Args:
        user(User): The user information return by authentication Depends
        payload: information which user input

        Return:
        the new user information
        """

        try:
            first_name = payload.first_name
            last_name = payload.last_name
            email = payload.email

            if first_name is not None:
                user.first_name = first_name
            if last_name is not None:
                user.last_name = last_name
            if user.email is not None:
                user.email = email

            await self.db.commit()
            await self.db.refresh(user)

            return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def update_user_phone_number(self, user: str, payload: UpdatePhoneInput):
        """
        Update user phone number

        Args:
        user(User): The user information return by authentication Depends
        payload: information which user input

        Return:
        the new user information
        """
        phone_number = payload.phone_number
        code = payload.code

        try:
            if code:
                code_send = self.complete_otp_phone_update(
                    code, phone_number, purpose="verify_phone"
                )
                if code_send:
                    user.phone_number = phone_number
                    self.db.commit()
                    self.db.refresh(user)
                    return user
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def send_register_sms_phone_update(
        self,
        phone_number: str,
        user: str,
        channel: str = "sms",
        purpose: str = "verify_phone",
    ) -> SmsVerificationOutput:

        now = datetime.now()
        stmt = select(OTP).where(
            OTP.target == phone_number,
            OTP.channel == channel,
            OTP.purpose == purpose,
            OTP.expires_at > now,
            OTP.is_used.is_(False),
        )
        result = await self.db.execute(stmt)
        otp = result.scalar_one_or_none()
        if otp:
            otp.is_used = True
            self.db.commit()

        code = generate_code()
        code_hash = hoc(code)
        expires_at = datetime.now() + timedelta(minutes=env.OTP_EXPIRE_MINUTES)
        new_otp = OTP(
            user_id=user.id,
            channel=channel,
            target=phone_number,
            purpose=purpose,
            code_hash=code_hash,
            expires_at=expires_at,
            last_sent_at=now,
        )
        self.db.add(new_otp)
        await self.db.commit()

        send_message = send_otp_sms(phone_number, code)
        print(send_message)

        return SmsVerificationOutput(
            phone_number=phone_number, prompt="verification code sent"
        )

    async def delete_user(self, user: str):
        """
        Delete user by her/him self
        Finally User be deactivated in db not delete

        Arg:
        User object including user_id

        Return:
        some message with successfully concept
        """

        try:
            user.is_activated = Fals
            await self.db.commit()

            return {"messege": "user with successfully delete"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )

    async def user_teams(self, user:str):
        """
        User teams which return all teams for user
        
        Arg:
        user: user information 

        Return:
        a list of the team
        """
        try:
            stmt = select(TeamModel).join(TeamUser).where(TeamUser.user_id == user.id)
            result = await self.db.execute(stmt)
            teams = result.all()
            if teams is None:
                return {
                    "message": "no team found for this user"
                }
            return teams
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})

    async def user_projects(self, user:str):
        """
        User teams which return all teams for user
        
        Arg:
        user: user information 

        Return:
        a list of the team
        """
        try:
            stmt = (
                select(ProjectModel)
                .join(ProjectUser, ProjectUser.project_id == ProjectModel.id)
                .where(ProjectUser.user_id == user.id)
            )
            result = await self.db.execute(stmt)
            projects = result.all()
            if projects is None:
                return {
                    "message": "no team found for this user"
                }
            return projects
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})
    
    async def user_tasks(self, user:str):
        """
        User tasks which return all tasks for user
        
        Arg:
        user: user information 

        Return:
        a list of the task
        """
        try:
            stmt = (
                select(TaskModel)
                .join(UserTask, UserTask.task_id == TaskModel.id)
                .where(UserTask.user_id == user.id)
            )
            result = await self.db.execute(stmt)
            tasks = result.all()
            if tasks is None:
                return {
                    "message": "no team found for this user"
                }
            return tasks
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)})

