from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.auth import ApiResponse
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("", response_model=ApiResponse)
def get_user_notifications(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    notifications = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).all()
    results = [NotificationOut.model_validate(n).model_dump() for n in notifications]
    return ApiResponse(success=True, message=f"Loaded {len(results)} notifications", data={"notifications": results})

@router.get("/unread", response_model=ApiResponse)
def get_unread_notifications_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).count()
    return ApiResponse(success=True, message="Unread count loaded", data={"unread_count": count})

@router.put("/{id}/read", response_model=ApiResponse)
def mark_notification_as_read(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == id, Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.is_read = True
    db.commit()
    return ApiResponse(success=True, message="Notification marked as read")

@router.put("/read-all", response_model=ApiResponse)
def mark_all_notifications_as_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return ApiResponse(success=True, message="All notifications marked as read")
