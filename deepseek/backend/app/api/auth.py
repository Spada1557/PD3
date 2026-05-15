from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Неверный email или пароль"})
    if user.status.value == "inactive":
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Пользователь деактивирован"})

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "name": user.name, "email": user.email, "role": user.role.value}
    )


@router.get("/me", response_model=UserResponse)
def me(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user["id"]).first()
    return db_user


@router.post("/register", response_model=UserResponse)
def register(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Пользователь с таким email уже существует"})

    from app.models import UserRole, UserStatus
    user = User(
        name=body.name,
        email=body.email,
        password_hash=hash_password(body.password),
        role=UserRole(body.role),
        status=UserStatus(body.status),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
