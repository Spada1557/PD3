from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Warehouse
from enamelware.schemas import WarehouseCreate, WarehouseOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=dict)
def list_warehouses(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Warehouse)
    total = query.count()
    warehouses = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [WarehouseOut.model_validate(w) for w in warehouses]}


@router.get("/all", response_model=list[WarehouseOut])
def list_all_warehouses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Warehouse).all()


@router.get("/{warehouse_id}", response_model=WarehouseOut)
def get_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Warehouse not found"})
    return w


@router.post("", response_model=WarehouseOut, status_code=status.HTTP_201_CREATED)
def create_warehouse(data: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    existing = db.query(Warehouse).filter(Warehouse.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Warehouse already exists"})
    w = Warehouse(name=data.name, address=data.address, is_active=data.is_active)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


@router.put("/{warehouse_id}", response_model=WarehouseOut)
def update_warehouse(warehouse_id: int, data: WarehouseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Warehouse not found"})
    existing = db.query(Warehouse).filter(Warehouse.name == data.name, Warehouse.id != warehouse_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Warehouse name already exists"})
    w.name = data.name
    w.address = data.address
    w.is_active = data.is_active
    db.commit()
    db.refresh(w)
    return w


@router.delete("/{warehouse_id}")
def delete_warehouse(warehouse_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    w = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not w:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Warehouse not found"})
    from enamelware.models import Stock
    if db.query(Stock).filter(Stock.warehouse_id == warehouse_id).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_references", "message": "Cannot delete warehouse with stock"})
    db.delete(w)
    db.commit()
    return {"message": "Warehouse deleted"}