from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification
from app.schemas import NotificationResponse, PaginatedResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=PaginatedResponse)
def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    unread_only: bool = False,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(Notification)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    q = q.order_by(Notification.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[NotificationResponse.model_validate(n) for n in items])


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"count": count}


@router.post("/{notification_id}/read")
def mark_read(notification_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if n:
        n.is_read = True
        db.commit()
    return {"message": "ok"}


@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    db.query(Notification).filter(Notification.is_read == False).update({Notification.is_read: True})
    db.commit()
    return {"message": "Все уведомления отмечены как прочитанные"}
