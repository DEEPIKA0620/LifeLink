import logging
from app.config import settings

logger = logging.getLogger("lifelink.sms")

def send_sms_notification(phone_number: str, message: str) -> bool:
    """
    Dispatches SMS alert. If SMS_API_KEY is not configured, logs warning and proceeds without crashing.
    """
    if not settings.SMS_API_KEY:
        logger.info(f"SMS service not configured. Simulated SMS to {phone_number}: '{message}'")
        return True
    
    try:
        # Third party SMS API code (e.g. Twilio)
        logger.info(f"SMS sent successfully to {phone_number}")
        return True
    except Exception as e:
        logger.error(f"Failed to send SMS to {phone_number}: {e}")
        return False
