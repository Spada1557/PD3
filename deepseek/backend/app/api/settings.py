from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Settings as DBSettings
from app.schemas import SettingsItemResponse, SettingsUpdateRequest, DatabaseConfigRequest, PaginatedResponse
from app.api.deps import get_current_user, require_role
from app.config import settings as app_settings
import os

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])


@router.get("")
def get_settings(db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    items = db.query(DBSettings).all()
    result = {s.key: s.value for s in items}

    result["current_database_url"] = _mask_password(app_settings.DATABASE_URL)

    return {"data": result}


@router.put("")
def update_settings(body: SettingsUpdateRequest, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    s = db.query(DBSettings).filter(DBSettings.key == body.key).first()
    if s:
        s.value = body.value
    else:
        s = DBSettings(key=body.key, value=body.value)
        db.add(s)
    db.commit()
    return {"message": "Настройка обновлена", "key": body.key, "value": body.value}


@router.put("/batch")
def update_batch_settings(settings_dict: dict, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    for key, value in settings_dict.items():
        s = db.query(DBSettings).filter(DBSettings.key == key).first()
        if s:
            s.value = str(value)
        else:
            db.add(DBSettings(key=key, value=str(value)))
    db.commit()
    return {"message": "Настройки обновлены"}


@router.post("/database/test")
def test_database_connection(body: DatabaseConfigRequest, user: dict = Depends(require_role("admin"))):
    from sqlalchemy import create_engine as sql_create_engine
    from sqlalchemy.exc import SQLAlchemyError

    test_url = body.database_url

    if not test_url:
        raise HTTPException(status_code=400, detail={"error": "invalid_url", "message": "Строка подключения не указана"})

    if "sqlite" not in test_url and "postgresql" not in test_url:
        raise HTTPException(status_code=400, detail={"error": "unsupported_db", "message": "Поддерживаются только SQLite и PostgreSQL"})

    try:
        test_engine = sql_create_engine(
            test_url,
            connect_args={"check_same_thread": False} if "sqlite" in test_url else {},
            pool_pre_ping=True,
        )
        conn = test_engine.connect()
        conn.close()
        return {"message": "Подключение успешно", "engine": "sqlite" if "sqlite" in test_url else "postgresql"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail={"error": "connection_failed", "message": f"Ошибка подключения: {str(e)}"})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": "connection_failed", "message": f"Ошибка подключения: {str(e)}"})


@router.post("/database/switch")
def switch_database(body: DatabaseConfigRequest, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    test_url = body.database_url
    if not test_url:
        raise HTTPException(status_code=400, detail={"error": "invalid_url", "message": "Строка подключения не указана"})

    try:
        # Update env
        os.environ["DATABASE_URL"] = test_url
        app_settings.DATABASE_URL = test_url

        # Store in DB settings for persistence
        s = db.query(DBSettings).filter(DBSettings.key == "database_url").first()
        if s:
            s.value = test_url
        else:
            db.add(DBSettings(key="database_url", value=test_url, description="Строка подключения к базе данных"))
        db.commit()

        return {
            "message": "Строка подключения обновлена. Перезапустите сервер для применения изменений.",
            "new_url": _mask_password(test_url),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "switch_failed", "message": str(e)})


def _mask_password(url: str) -> str:
    if "@" in url and "://" in url:
        parts = url.split("@")
        proto_creds = parts[0].split("://")
        if len(proto_creds) == 2:
            creds = proto_creds[1].split(":")
            if len(creds) == 2:
                masked = f"{proto_creds[0]}://{creds[0]}:****@{parts[1]}"
                return masked
    return url
