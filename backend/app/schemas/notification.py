from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    reference_id: Optional[int] = None
    is_read: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
