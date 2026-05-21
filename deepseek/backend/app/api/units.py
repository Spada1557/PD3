from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Unit
from app.schemas import UnitCreate, UnitUpdate, UnitResponse, PaginatedResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/units", tags=["units"])


@router.get("", response_model=PaginatedResponse)
def list_units(page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    q = db.query(Unit)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[UnitResponse.model_validate(u) for u in items])


@router.post("", response_model=UnitResponse, status_code=201)
def create_unit(body: UnitCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    existing = db.query(Unit).filter(Unit.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Единица измерения с таким названием уже существует"})
    u = Unit(**body.model_dump())
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.put("/{unit_id}", response_model=UnitResponse)
def update_unit(unit_id: int, body: UnitUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    u = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Единица измерения не найдена"})
    if body.name is not None:
        u.name = body.name
    if body.short_name is not None:
        u.short_name = body.short_name
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{unit_id}")
def delete_unit(unit_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    u = db.query(Unit).filter(Unit.id == unit_id).first()
    if not u:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Единица измерения не найдена"})
    if u.products and len(u.products) > 0:
        raise HTTPException(status_code=400, detail={"error": "has_products", "message": "Нельзя удалить единицу измерения, используемую в товарах"})
    db.delete(u)
    db.commit()
    return {"message": "Единица измерения удалена"}
