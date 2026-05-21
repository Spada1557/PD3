from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Supplier
from app.schemas import SupplierCreate, SupplierUpdate, SupplierResponse, PaginatedResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/suppliers", tags=["suppliers"])


@router.get("", response_model=PaginatedResponse)
def list_suppliers(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    from sqlalchemy import or_
    q = db.query(Supplier)
    if search:
        q = q.filter(or_(Supplier.name.ilike(f"%{search}%"), Supplier.inn.ilike(f"%{search}%")))
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[SupplierResponse.model_validate(s) for s in items])


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Поставщик не найден"})
    return s


@router.post("", response_model=SupplierResponse, status_code=201)
def create_supplier(body: SupplierCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    s = Supplier(**body.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(supplier_id: int, body: SupplierUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Поставщик не найден"})
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    db.commit()
    db.refresh(s)
    return s


@router.delete("/{supplier_id}")
def delete_supplier(supplier_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Поставщик не найден"})
    s.status = "inactive"
    db.commit()
    return {"message": "Поставщик деактивирован"}
