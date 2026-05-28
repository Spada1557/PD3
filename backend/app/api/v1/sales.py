from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.services.document_service import generate_number, post_sale, cancel_sale
from app import crud, schemas, models

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.get("", response_model=schemas.PaginatedResponse)
def list_sales(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    client_id: int | None = None,
    db: Session = Depends(get_db),
):
    result = crud.get_sales(db, page=page, per_page=per_page, status=status, date_from=date_from, date_to=date_to, client_id=client_id)
    return jsonable_encoder(result)


@router.get("/{sale_id}", response_model=schemas.SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    s = crud.get_sale(db, sale_id)
    if not s:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    return s


@router.post("", response_model=schemas.SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    obj: schemas.SaleCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    number = generate_number(db, "ПР")
    return crud.create_sale(db, obj, number, user.id)


@router.put("/{sale_id}", response_model=schemas.SaleOut)
def update_sale(
    sale_id: int,
    obj: schemas.SaleUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_sale(db, sale_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    try:
        return crud.update_sale(db, db_obj, obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{sale_id}")
def delete_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_sale(db, sale_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    try:
        crud.delete_sale(db, db_obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "Удалено"}


@router.post("/{sale_id}/post", response_model=schemas.SaleOut)
def post_sale_endpoint(
    sale_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_sale(db, sale_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    try:
        return post_sale(db, db_obj, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{sale_id}/cancel", response_model=schemas.SaleOut)
def cancel_sale_endpoint(
    sale_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_sale(db, sale_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продажа не найдена")
    try:
        return cancel_sale(db, db_obj, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
