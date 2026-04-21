from sms_ir import SmsIr

from app.config import settings as env
import secrets
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession

from sms_ir import SmsIr
from fastapi import HTTPException, status

sms_ir = SmsIr(
    env.SMS_IR_API_KAY_OTP,
    env.LINE_NUMBER_OTP,
)


def generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"


def hash_otp_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def send_otp_sms(phone_number: str, code: str):

    try:
        response = sms_ir.send_verify_code(
            number=phone_number,
            template_id=env.OTP_TEMPLATE_ID,
            parameters=[
                {
                    "name": "OTP",
                    "value": code,
                },
            ],
        )
        print(type(response))
        print(response)
        return {"message": "otp sent"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail={"error": str(e)}
        )


#     sms_ir.report_message(
#         message_id,
#     )
