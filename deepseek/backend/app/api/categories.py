from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse, PaginatedResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


@router.get("", response_model=PaginatedResponse)
def list_categories(page: int = Query(1, ge=1), per_page: int = Query(50, ge=1, le=100), db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    q = db.query(Category)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[CategoryResponse.model_validate(c) for c in items])


@router.get("/{cat_id}", response_model=CategoryResponse)
def get_category(cat_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Category).filter(Category.id == cat_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Категория не найдена"})
    return c


@router.post("", response_model=CategoryResponse, status_code=201)
def create_category(body: CategoryCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    existing = db.query(Category).filter(Category.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail={"error": "duplicate", "message": "Категория с таким названием уже существует"})
    c = Category(**body.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.put("/{cat_id}", response_model=CategoryResponse)
def update_category(cat_id: int, body: CategoryUpdate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Category).filter(Category.id == cat_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Категория не найдена"})
    if body.name is not None:
        c.name = body.name
    if body.description is not None:
        c.description = body.description
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{cat_id}")
def delete_category(cat_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    c = db.query(Category).filter(Category.id == cat_id).first()
    if not c:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Категория не найдена"})
    if c.products and len(c.products) > 0:
        raise HTTPException(status_code=400, detail={"error": "has_products", "message": "Нельзя удалить категорию, в которой есть товары"})
    db.delete(c)
    db.commit()
    return {"message": "Категория удалена"}
