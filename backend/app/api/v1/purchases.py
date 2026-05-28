from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.services.document_service import generate_number, post_purchase, cancel_purchase
from app import crud, schemas, models

router = APIRouter(prefix="/purchases", tags=["Purchases"])


@router.get("", response_model=schemas.PaginatedResponse)
def list_purchases(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    supplier_id: int | None = None,
    db: Session = Depends(get_db),
):
    result = crud.get_purchases(db, page=page, per_page=per_page, status=status, date_from=date_from, date_to=date_to, supplier_id=supplier_id)
    return jsonable_encoder(result)


@router.get("/{purchase_id}", response_model=schemas.PurchaseOut)
def get_purchase(purchase_id: int, db: Session = Depends(get_db)):
    p = crud.get_purchase(db, purchase_id)
    if not p:
        raise HTTPException(status_code=404, detail="Приход не найден")
    return p


@router.post("", response_model=schemas.PurchaseOut, status_code=status.HTTP_201_CREATED)
def create_purchase(
    obj: schemas.PurchaseCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    number = generate_number(db, "ПУ")
    return crud.create_purchase(db, obj, number, user.id)


@router.put("/{purchase_id}", response_model=schemas.PurchaseOut)
def update_purchase(
    purchase_id: int,
    obj: schemas.PurchaseUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    db_obj = crud.get_purchase(db, purchase_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Приход не найден")
    try:
        return crud.update_purchase(db, db_obj, obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{purchase_id}")
def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    db_obj = crud.get_purchase(db, purchase_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Приход не найден")
    try:
        crud.delete_purchase(db, db_obj)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "Удалено"}


@router.post("/{purchase_id}/post", response_model=schemas.PurchaseOut)
def post_purchase_endpoint(
    purchase_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    db_obj = crud.get_purchase(db, purchase_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Приход не найден")
    try:
        return post_purchase(db, db_obj, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{purchase_id}/cancel", response_model=schemas.PurchaseOut)
def cancel_purchase_endpoint(
    purchase_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    db_obj = crud.get_purchase(db, purchase_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Приход не найден")
    try:
        return cancel_purchase(db, db_obj, user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
