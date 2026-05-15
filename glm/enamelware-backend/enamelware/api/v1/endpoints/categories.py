from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Category, Product
from enamelware.schemas import CategoryCreate, CategoryOut, ErrorResponse
from enamelware.auth import get_current_user, require_role
from enamelware.models import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", response_model=dict)
def list_categories(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Category)
    total = query.count()
    categories = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [CategoryOut.model_validate(c) for c in categories]}


@router.get("/all", response_model=list[CategoryOut])
def list_all_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Category).all()


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Category not found"})
    return cat


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    existing = db.query(Category).filter(Category.name == data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Category with this name already exists"})
    cat = Category(name=data.name, description=data.description)
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(category_id: int, data: CategoryCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Category not found"})
    existing = db.query(Category).filter(Category.name == data.name, Category.id != category_id).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": "Category with this name already exists"})
    cat.name = data.name
    cat.description = data.description
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Category not found"})
    products_count = db.query(Product).filter(Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_references", "message": "Cannot delete category with products"})
    db.delete(cat)
    db.commit()
    return {"message": "Category deleted"}