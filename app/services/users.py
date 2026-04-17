



import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.smsir import (
    hash_otp_code as hoc,
    generate_code
)

logger = logging.getLogger(__name__)





def send_sms(phone_number: str, code: str) -> None:
    try:
        #send sms func
        return False
    except Exception:
        logger.warning("SMS Provider failed, printing code for %s", phone_number)
        logger.info("SMS to %s: your verification code is %s", phone_number, code)
    










class UsersOpration:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
    
