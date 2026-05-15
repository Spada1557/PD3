import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from enamelware.database import get_db
from enamelware.models import Product, Stock, StockMovement, Category, Unit
from enamelware.schemas import ProductCreate, ProductUpdate, ProductOut, StockOut, StockMovementOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User
from enamelware.enums import MovementType, DocumentType, ProductStatus

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=dict)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    search: str = None,
    category_id: int = None,
    status_filter: str = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Product)
    if search:
        query = query.filter(or_(Product.name.ilike(f"%{search}%"), Product.article.ilike(f"%{search}%")))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if status_filter:
        query = query.filter(Product.status == status_filter)
    total = query.count()
    products = query.order_by(Product.name).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [ProductOut.model_validate(p) for p in products]}


@router.get("/all", response_model=list[ProductOut])
def list_all_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Product).filter(Product.status == ProductStatus.active).all()


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Product not found"})
    return p


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(data: ProductCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager", "warehouse"))):
    existing = db.query(Product).filter(Product.article == data.article).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": f"Product with article '{data.article}' already exists"})
    p = Product(
        name=data.name, article=data.article, category_id=data.category_id,
        unit_id=data.unit_id, price=data.price, cost=data.cost,
        min_stock=data.min_stock, status=data.status, image_path=data.image_path,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    from enamelware.models import Warehouse
    warehouses = db.query(Warehouse).all()
    for w in warehouses:
        stock = Stock(product_id=p.id, warehouse_id=w.id, quantity=0, reserved=0, avg_cost=data.cost)
        db.add(stock)
    db.commit()
    return p


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, data: ProductUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager", "warehouse"))):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Product not found"})
    if data.article and data.article != p.article:
        existing = db.query(Product).filter(Product.article == data.article).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "already_exists", "message": f"Product with article '{data.article}' already exists"})
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return p


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Product not found"})
    movements_count = db.query(StockMovement).filter(StockMovement.product_id == product_id).count()
    if movements_count > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "has_movements", "message": "Cannot delete product with stock movements"})
    db.query(Stock).filter(Stock.product_id == product_id).delete()
    db.delete(p)
    db.commit()
    return {"message": "Product deleted"}


@router.post("/{product_id}/image")
def upload_product_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager", "warehouse"))):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Product not found"})
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "invalid_format", "message": "Only JPG/PNG images allowed"})
    contents = file.file.read()
    if len(contents) > 2 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "file_too_large", "message": "Image must be under 2MB"})
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    ext = "jpg" if file.content_type == "image/jpeg" else "png"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(contents)
    p.image_path = filename
    db.commit()
    return {"image_path": filename}