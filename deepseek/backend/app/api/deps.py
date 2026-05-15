from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.security import decode_access_token
from app.models import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Недействительный или просроченный токен"})

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Недействительный токен"})

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or user.status == "inactive":
        raise HTTPException(status_code=401, detail={"error": "unauthorized", "message": "Пользователь не найден или деактивирован"})

    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role.value, "status": user.status.value}


def require_role(*roles: str):
    def checker(user: dict = Depends(get_current_user)):
        if user["role"] not in roles:
            raise HTTPException(status_code=403, detail={"error": "forbidden", "message": "Недостаточно прав для выполнения операции"})
        return user
    return checker
