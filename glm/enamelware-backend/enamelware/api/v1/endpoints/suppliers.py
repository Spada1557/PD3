from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Supplier
from enamelware.schemas import SupplierCreate, SupplierOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("", response_model=dict)
def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    query = db.query(Supplier)
    if search:
        query = query.filter(Supplier.name.ilike(f"%{search}%"))
    total = query.count()
    suppliers = query.order_by(Supplier.name).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [SupplierOut.model_validate(s) for s in suppliers]}


@router.get("/all", response_model=list[SupplierOut])
def list_all_suppliers(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    return db.query(Supplier).filter(Supplier.is_active == True).all()


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Supplier not found"})
    return s


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    existing = db.query(Supplier).filter(Supplier.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Supplier already exists"})
    s = Supplier(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, data: SupplierCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Supplier not found"})
    existing = db.query(Supplier).filter(Supplier.name == data.name, Supplier.id != supplier_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Supplier name already exists"})
    for key, value in data.model_dump().items():
        setattr(s, key, value)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Supplier not found"})
    from enamelware.models import Purchase
    if db.query(Purchase).filter(Purchase.supplier_id == supplier_id).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_references", "message": "Cannot delete supplier with purchases"})
    db.delete(s)
    db.commit()
    return {"message": "Supplier deleted"}