from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app import crud, schemas, models
import shutil, os, uuid

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("", response_model=schemas.PaginatedResponse)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    category_id: int | None = None,
    status: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    result = crud.get_products(db, page=page, per_page=per_page, category_id=category_id, status=status, search=search)
    return jsonable_encoder(result)


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = crud.get_product(db, product_id)
    if not p:
        raise HTTPException(status_code=404, detail="Продукция не найдена")
    return p


@router.post("", response_model=schemas.ProductOut)
def create_product(
    obj: schemas.ProductCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    existing = crud.get_product_by_article(db, obj.article)
    if existing:
        raise HTTPException(status_code=400, detail="Артикул уже существует")
    return crud.create_product(db, obj)


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    obj: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_product(db, product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продукция не найдена")
    if obj.article:
        existing = crud.get_product_by_article(db, obj.article)
        if existing and existing.id != product_id:
            raise HTTPException(status_code=400, detail="Артикул уже занят")
    return crud.update_product(db, db_obj, obj)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    db_obj = crud.get_product(db, product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продукция не найдена")
    movements = db.query(models.StockMovement).filter(models.StockMovement.product_id == product_id).first()
    if movements:
        raise HTTPException(status_code=400, detail="Нельзя удалить: есть движения по складу")
    crud.delete_product(db, db_obj)
    return {"detail": "Удалено"}


@router.post("/{product_id}/upload-image")
def upload_image(product_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: models.User = Depends(require_role(["admin", "manager"]))):
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(status_code=400, detail="Только JPG/PNG")
    db_obj = crud.get_product(db, product_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Продукция не найдена")
    ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    db_obj.image_path = f"/uploads/{filename}"
    db.commit()
    return {"image_path": db_obj.image_path}
