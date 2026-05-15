from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, UserRole, UserStatus
from app.schemas import UserCreate, UserUpdate, UserResponse, PaginatedResponse
from app.utils.security import hash_password
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("", response_model=PaginatedResponse)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    role: str = None,
    status: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(require_role("admin")),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    if status:
        q = q.filter(User.status == status)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[UserResponse.model_validate(u) for u in items])


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Пользователь не найден"})
    return u


@router.post("", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Пользователь с таким email уже существует"})
    u = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=UserRole(body.role),
        status=UserStatus(body.status),
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Пользователь не найден"})
    if body.name is not None:
        u.name = body.name
    if body.email is not None:
        existing = db.query(User).filter(User.email == body.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Пользователь с таким email уже существует"})
        u.email = body.email
    if body.password is not None:
        u.password_hash = hash_password(body.password)
    if body.role is not None:
        u.role = UserRole(body.role)
    if body.status is not None:
        u.status = UserStatus(body.status)
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Пользователь не найден"})
    has_purchases = u.purchases and len(u.purchases) > 0
    has_sales = u.sales and len(u.sales) > 0
    if has_purchases or has_sales:
        raise HTTPException(status_code=400, detail={"error": "has_documents", "message": "Нельзя удалить пользователя — он является автором документов"})
    u.status = UserStatus.inactive
    db.commit()
    return {"message": "Пользователь деактивирован"}
