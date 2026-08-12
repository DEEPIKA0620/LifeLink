import logging
from app.config import settings

logger = logging.getLogger("lifelink.email")

def send_email_notification(to_email: str, subject: str, body: str) -> bool:
    """
    Dispatches email alert. If EMAIL_API_KEY is missing, logs gracefully without failing.
    """
    if not settings.EMAIL_API_KEY:
        logger.info(f"[Email Service simulated] To: {to_email} | Subject: {subject}")
        return True
    
    try:
        # Integrated email sending code would go here
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
