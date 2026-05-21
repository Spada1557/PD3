from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Warehouse
from app.schemas import WarehouseCreate, WarehouseUpdate, WarehouseResponse, PaginatedResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/warehouses", tags=["warehouses"])


@router.get("", response_model=PaginatedResponse)
def list_warehouses(page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    q = db.query(Warehouse)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[WarehouseResponse.model_validate(w) for w in items])


@router.post("", response_model=WarehouseResponse, status_code=201)
def create_warehouse(body: WarehouseCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    existing = db.query(Warehouse).filter(Warehouse.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Склад с таким названием уже существует"})
    w = Warehouse(**body.model_dump())
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@router.put("/{wh_id}", response_model=WarehouseResponse)
def update_warehouse(wh_id: int, body: WarehouseUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    w = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    if not w:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Склад не найден"})
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(w, field, value)
    db.commit()
    db.refresh(w)
    return w


@router.delete("/{wh_id}")
def delete_warehouse(wh_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    w = db.query(Warehouse).filter(Warehouse.id == wh_id).first()
    if not w:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Склад не найден"})
    from app.models import Stock
    has_stock = db.query(Stock).filter(Stock.warehouse_id == wh_id).count() > 0
    if has_stock:
        raise HTTPException(status_code=400, detail={"error": "has_stock", "message": "Нельзя удалить склад с остатками товаров"})
    db.delete(w)
    db.commit()
    return {"message": "Склад удалён"}
