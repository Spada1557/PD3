from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.core.config import settings
from app import crud, schemas, models

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/company", response_model=schemas.CompanySettings)
def get_company(db: Session = Depends(get_db), user: models.User = Depends(require_role("admin"))):
    return crud.get_company_settings(db)


@router.put("/company", response_model=schemas.CompanySettings)
def update_company(data: schemas.CompanySettings, db: Session = Depends(get_db), user: models.User = Depends(require_role("admin"))):
    return crud.save_company_settings(db, data)


@router.get("/db")
def get_db_config(user: models.User = Depends(require_role("admin"))) -> dict:
    return {"db_url": settings.DATABASE_URL}


@router.put("/db")
def update_db_config(payload: dict, user: models.User = Depends(require_role("admin"))) -> dict:
    # В реальном проекте можно перезаписывать .env и перезагружать engine.
    # Здесь возвращаем информацию, что настройка принята.
    return {"message": "Для применения новой строки подключения требуется перезапуск сервиса", "db_url": payload.get("db_url")}
