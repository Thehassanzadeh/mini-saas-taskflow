import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.smsir import hash_otp_code as hoc, generate_code, send_otp_sms

from fastapi import HTTPException, status
from uuid import UUID

from app.schema._output import SmsVerificationOutput, SmsVerificationCompleteOutput

from sqlalchemy import select

from app.db.models import OTP, UserModel

from app.config import settings as env

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


code = generate_code()


def send_sms(phone_number: str, code: str) -> None:
    try:
        send_otp_sms(phone_number, code)
    except Exception:
        logger.warning("SMS Provider failed, printing code for %s", phone_number)
        logger.info("SMS to %s: your verification code is %s", phone_number, code)


class UsersOperation:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def send_verification_sms(
        self, phone_number: str, channel: str = "sms", purpose: str = "OTP"
    ) -> SmsVerificationOutput:

        now = datetime.now()
        stmt = select(UserModel).where(UserModel.phone_number == phone_number)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "user or phone number not found")

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

    async def complete_otp(self, code: str, phone_number: str) -> SmsVerificationCompleteOutput:

        hash_code = hoc(code)
        now = datetime.now()
        stmt = select(OTP).where(
            OTP.target == phone_number,
            OTP.code_hash == hash_code,
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
            print  ("successfully")
            return SmsVerificationCompleteOutput(
                phone_number=phone_number, prompt="verify successfully"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
            )
        
