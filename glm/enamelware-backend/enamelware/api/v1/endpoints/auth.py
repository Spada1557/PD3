from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import User, Notification
from enamelware.schemas import (
    UserCreate, UserUpdate, UserOut, LoginRequest, TokenResponse, NotificationOut, ErrorResponse
)
from enamelware.auth import (
    hash_password, verify_password, create_access_token, get_current_user, require_role
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"error": "unauthorized", "message": "Invalid email or password"})
    if user.status.value == "inactive":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"error": "forbidden", "message": "Account is deactivated"})
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/notifications", response_model=list[NotificationOut])
def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifs = db.query(Notification).filter(Notification.user_id == current_user.id).order_by(Notification.created_at.desc()).limit(20).all()
    return notifs


@router.put("/notifications/{notif_id}/read")
def mark_notification_read(notif_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id, Notification.user_id == current_user.id).first()
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Notification not found"})
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}


@router.put("/notifications/read-all")
def mark_all_notifications_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}


router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("", response_model=dict)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    role: str = None,
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status_filter:
        query = query.filter(User.status == status_filter)
    total = query.count()
    users = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [UserOut.model_validate(u) for u in users]}


@router_users.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "User not found"})
    return user


@router_users.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Email already registered"})
    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router_users.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "User not found"})
    from enamelware.models import Purchase, Sale
    purchases_count = db.query(Purchase).filter(Purchase.created_by == user_id).count()
    sales_count = db.query(Sale).filter(Sale.created_by == user_id).count()
    if data.status == "inactive" and (purchases_count > 0 or sales_count > 0):
        user.status = "inactive"
        db.commit()
        db.refresh(user)
        return user
    for key, value in data.model_dump(exclude_unset=True).items():
        if key == "email" and value:
            existing = db.query(User).filter(User.email == value, User.id != user_id).first()
            if existing:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Email already in use"})
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user