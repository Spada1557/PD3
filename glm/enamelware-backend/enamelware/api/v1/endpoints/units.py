from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Unit
from enamelware.schemas import UnitCreate, UnitOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User

router = APIRouter(prefix="/units", tags=["Units"])


@router.get("", response_model=dict)
def list_units(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Unit)
    total = query.count()
    units = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [UnitOut.model_validate(u) for u in units]}


@router.get("/all", response_model=list[UnitOut])
def list_all_units(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Unit).all()


@router.get("/{unit_id}", response_model=UnitOut)
def get_unit(unit_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    u = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Unit not found"})
    return u


@router.post("", response_model=UnitOut, status_code=status.HTTP_201_CREATED)
def create_unit(data: UnitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    existing = db.query(Unit).filter((Unit.name == data.name) | (Unit.short_name == data.short_name)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Unit with this name or short_name already exists"})
    u = Unit(name=data.name, short_name=data.short_name)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/{unit_id}", response_model=UnitOut)
def update_unit(unit_id: int, data: UnitCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    u = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Unit not found"})
    existing = db.query(Unit).filter(((Unit.name == data.name) | (Unit.short_name == data.short_name)) & (Unit.id != unit_id)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Unit name already exists"})
    u.name = data.name
    u.short_name = data.short_name
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{unit_id}")
def delete_unit(unit_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    u = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Unit not found"})
    from enamelware.models import Product
    if db.query(Product).filter(Product.unit_id == unit_id).count() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_references", "message": "Cannot delete unit with products"})
    db.delete(u)
    db.commit()
    return {"message": "Unit deleted"}