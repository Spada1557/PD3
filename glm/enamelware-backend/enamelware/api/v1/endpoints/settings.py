import io
import csv
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import AppSettings
from enamelware.schemas import AppSettingsUpdate, AppSettingsOut
from enamelware.auth import require_role
from enamelware.models import User
from enamelware.enums import UserRole, ProductStatus
import openpyxl

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=AppSettingsOut)
def get_settings(db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.put("", response_model=AppSettingsOut)
def update_settings(data: AppSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(settings, key, value)
    db.commit()
    db.refresh(settings)
    return settings


router_import = APIRouter(prefix="/import", tags=["Import"])


@router_import.post("/products")
async def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail={"error": "invalid_format", "message": "Only .xlsx and .csv files are supported"})

    from enamelware.models import Product, Category, Unit

    content = await file.read()
    rows = []

    if file.filename.endswith(".xlsx"):
        wb = openpyxl.load_workbook(io.BytesIO(content))
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            if row[0]:
                rows.append(row)
    else:
        decoded = content.decode("utf-8")
        reader = csv.reader(io.StringIO(decoded), delimiter=";")
        next(reader, None)
        for row in reader:
            if row and row[0]:
                rows.append(row)

    created = 0
    errors = []
    for i, row in enumerate(rows):
        try:
            name = str(row[0]).strip()
            article = str(row[1]).strip()
            category_name = str(row[2]).strip() if len(row) > 2 and row[2] else None
            unit_name = str(row[3]).strip() if len(row) > 3 and row[3] else None
            price = float(row[4]) if len(row) > 4 and row[4] else 0.0
            cost = float(row[5]) if len(row) > 5 and row[5] else 0.0
            min_stock = int(float(row[6])) if len(row) > 6 and row[6] else 10

            existing = db.query(Product).filter(Product.article == article).first()
            if existing:
                errors.append(f"Row {i+2}: Article '{article}' already exists")
                continue

            category_id = None
            if category_name:
                cat = db.query(Category).filter(Category.name == category_name).first()
                if cat:
                    category_id = cat.id

            unit_id = None
            if unit_name:
                u = db.query(Unit).filter(Unit.name == unit_name).first()
                if u:
                    unit_id = u.id

            product = Product(
                name=name, article=article, category_id=category_id,
                unit_id=unit_id, price=price, cost=cost, min_stock=min_stock,
                status=ProductStatus.active,
            )
            db.add(product)
            created += 1
        except Exception as e:
            errors.append(f"Row {i+2}: {str(e)}")

    db.commit()
    return {"created": created, "errors": errors, "total_rows": len(rows)}