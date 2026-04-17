from sms_ir import SmsIr

from app.config import settings as env
import secrets
import hashlib

from sms_ir import SmsIr
sms_ir = SmsIr(
env.SMS_IR_API_KAY_OTP,
env.LINE_NUMBER_OTP,
)

sms_ir.send_verify_code(number,template_id,parameters,)


sms_ir.report_message(message_id,)


sms_ir.get_credit()


sms_ir.get_line_numbers()


sms_ir.send_verify_code(
    number="+989111111111",
    template_id=10000,
    parameters=[
        {
            "name" : "code",
            "value": 12345,
        },
    ],
)



def generate_code() -> str:
    return f"{secrets.randbelow(900000) + 100000}"

def hash_otp_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()





