from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.models.user import User
from app.services.email_service import send_email_notification
from app.services.sms_service import send_sms_notification

def create_user_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "system",
    reference_id: int = None
) -> Notification:
    """
    Creates a database notification and triggers Email/SMS services if configured.
    """
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        reference_id=reference_id,
        is_read=False
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Fetch user for phone / email alerts
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        send_email_notification(user.email, f"[LifeLink Alert] {title}", message)
        send_sms_notification(user.phone, f"LifeLink Alert: {title} - {message}")

    return notification
