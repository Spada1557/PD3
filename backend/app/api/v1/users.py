from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app import crud, schemas, models

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=schemas.PaginatedResponse)
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role("admin")),
):
    result = crud.get_users(db, page=page, per_page=per_page)
    return jsonable_encoder(result)


@router.get("/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(require_role("admin"))):
    u = crud.get_user(db, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return u


@router.post("", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    obj: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    existing = crud.get_user_by_email(db, obj.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email уже занят")
    return crud.create_user(db, obj)


@router.put("/{user_id}", response_model=schemas.UserOut)
def update_user(
    user_id: int,
    obj: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    db_obj = crud.get_user(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Проверка на удаление (нельзя удалить, если автор документов) — здесь обновление статуса
    if obj.status == "inactive":
        # Нельзя деактивировать самого себя
        if db_obj.id == current_user.id:
            raise HTTPException(status_code=400, detail="Нельзя деактивировать самого себя")
    if obj.email:
        existing = crud.get_user_by_email(db, obj.email)
        if existing and existing.id != user_id:
            raise HTTPException(status_code=400, detail="Email уже занят")
    return crud.update_user(db, db_obj, obj)


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_role("admin")),
):
    db_obj = crud.get_user(db, user_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    # Запрет удаления, если пользователь — автор документов
    has_purchases = db.query(models.Purchase).filter(models.Purchase.created_by == user_id).first()
    has_sales = db.query(models.Sale).filter(models.Sale.created_by == user_id).first()
    if has_purchases or has_sales:
        raise HTTPException(status_code=400, detail="Нельзя удалить: пользователь является автором документов")
    crud.delete_user(db, db_obj)
    return {"detail": "Удалено"}
