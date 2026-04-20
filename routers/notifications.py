from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
import models
from database import get_db
from auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    id: int
    message: str
    type: str
    read: bool
    created_at: datetime
    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).limit(20).all()
    return notifications

@router.get("/unread")
def get_unread_count(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.read == False
    ).count()
    return {"unread_count": count}

@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.read = True
    db.commit()
    return {"message": "Notification marked as read"}
