from typing import List, Optional, TypeVar, Generic
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app import models, schemas

T = TypeVar("T", bound=models.Base)


def paginate(query, page: int = 1, per_page: int = 10):
    total = query.count()
    data = query.offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": data}


# ============================
# Users
# ============================
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(func.lower(models.User.email) == func.lower(email)).first()


def get_users(db: Session, page: int = 1, per_page: int = 10):
    return paginate(db.query(models.User).order_by(models.User.id.desc()), page, per_page)


def create_user(db: Session, obj: schemas.UserCreate) -> models.User:
    from app.core.security import get_password_hash
    db_obj = models.User(
        name=obj.name,
        email=obj.email,
        password_hash=get_password_hash(obj.password),
        role=models.UserRole(obj.role),
        status=models.UserStatus(obj.status),
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_user(db: Session, db_obj: models.User, obj: schemas.UserUpdate) -> models.User:
    from app.core.security import get_password_hash
    data = obj.model_dump(exclude_unset=True)
    if "password" in data and data["password"]:
        data["password_hash"] = get_password_hash(data.pop("password"))
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_user(db: Session, db_obj: models.User) -> None:
    db.delete(db_obj)
    db.commit()


# ============================
# References
# ============================
def get_categories(db: Session):
    return db.query(models.Category).order_by(models.Category.name).all()


def create_category(db: Session, obj: schemas.CategoryCreate) -> models.Category:
    db_obj = models.Category(name=obj.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_units(db: Session):
    return db.query(models.Unit).order_by(models.Unit.name).all()


def create_unit(db: Session, obj: schemas.UnitCreate) -> models.Unit:
    db_obj = models.Unit(name=obj.name)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_warehouses(db: Session):
    return db.query(models.Warehouse).order_by(models.Warehouse.name).all()


def create_warehouse(db: Session, obj: schemas.WarehouseCreate) -> models.Warehouse:
    db_obj = models.Warehouse(name=obj.name, is_default=obj.is_default)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_suppliers(db: Session, page: int = 1, per_page: int = 10, search: Optional[str] = None):
    q = db.query(models.Supplier).order_by(models.Supplier.name)
    if search:
        q = q.filter(models.Supplier.name.ilike(f"%{search}%"))
    return paginate(q, page, per_page)


def create_supplier(db: Session, obj: schemas.SupplierCreate) -> models.Supplier:
    db_obj = models.Supplier(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_supplier(db: Session, db_obj: models.Supplier, obj: schemas.SupplierUpdate) -> models.Supplier:
    data = obj.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_supplier(db: Session, db_obj: models.Supplier) -> None:
    db.delete(db_obj)
    db.commit()


def get_clients(db: Session, page: int = 1, per_page: int = 10, search: Optional[str] = None):
    q = db.query(models.Client).order_by(models.Client.name)
    if search:
        q = q.filter(models.Client.name.ilike(f"%{search}%"))
    return paginate(q, page, per_page)


def create_client(db: Session, obj: schemas.ClientCreate) -> models.Client:
    db_obj = models.Client(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_client(db: Session, db_obj: models.Client, obj: schemas.ClientUpdate) -> models.Client:
    data = obj.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_client(db: Session, db_obj: models.Client) -> None:
    db.delete(db_obj)
    db.commit()


# ============================
# Products
# ============================
def get_product(db: Session, product_id: int) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def get_product_by_article(db: Session, article: str) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.article == article).first()


def get_products(db: Session, page: int = 1, per_page: int = 10, category_id: Optional[int] = None, status: Optional[str] = None, search: Optional[str] = None):
    q = db.query(models.Product).order_by(models.Product.name)
    if category_id:
        q = q.filter(models.Product.category_id == category_id)
    if status:
        q = q.filter(models.Product.status == status)
    if search:
        q = q.filter(
            models.Product.name.ilike(f"%{search}%") | models.Product.article.ilike(f"%{search}%")
        )
    return paginate(q, page, per_page)


def create_product(db: Session, obj: schemas.ProductCreate, image_path: Optional[str] = None) -> models.Product:
    db_obj = models.Product(
        **obj.model_dump(),
        image_path=image_path,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_product(db: Session, db_obj: models.Product, obj: schemas.ProductUpdate) -> models.Product:
    data = obj.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_product(db: Session, db_obj: models.Product) -> None:
    db.delete(db_obj)
    db.commit()


# ============================
# Stock
# ============================
def get_stock(db: Session, page: int = 1, per_page: int = 10, warehouse_id: Optional[int] = None, product_id: Optional[int] = None):
    q = db.query(models.Stock).options(
        joinedload(models.Stock.product),
        joinedload(models.Stock.warehouse),
    ).order_by(models.Stock.id)
    if warehouse_id:
        q = q.filter(models.Stock.warehouse_id == warehouse_id)
    if product_id:
        q = q.filter(models.Stock.product_id == product_id)
    return paginate(q, page, per_page)


def get_stock_item(db: Session, product_id: int, warehouse_id: int) -> Optional[models.Stock]:
    return db.query(models.Stock).filter(
        models.Stock.product_id == product_id,
        models.Stock.warehouse_id == warehouse_id,
    ).first()


def get_or_create_stock(db: Session, product_id: int, warehouse_id: int) -> models.Stock:
    item = get_stock_item(db, product_id, warehouse_id)
    if not item:
        item = models.Stock(product_id=product_id, warehouse_id=warehouse_id, quantity=0, reserved=0, avg_cost=0)
        db.add(item)
        db.flush()
    return item


def get_stock_movements(db: Session, page: int = 1, per_page: int = 10, product_id: Optional[int] = None, warehouse_id: Optional[int] = None):
    q = db.query(models.StockMovement).options(
        joinedload(models.StockMovement.product),
        joinedload(models.StockMovement.warehouse),
        joinedload(models.StockMovement.user),
    ).order_by(models.StockMovement.created_at.desc())
    if product_id:
        q = q.filter(models.StockMovement.product_id == product_id)
    if warehouse_id:
        q = q.filter(models.StockMovement.warehouse_id == warehouse_id)
    return paginate(q, page, per_page)


# ============================
# Purchases
# ============================
def get_purchase(db: Session, purchase_id: int) -> Optional[models.Purchase]:
    return db.query(models.Purchase).filter(models.Purchase.id == purchase_id).first()


def get_purchases(db: Session, page: int = 1, per_page: int = 10, status: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, supplier_id: Optional[int] = None):
    q = db.query(models.Purchase).order_by(models.Purchase.id.desc())
    if status:
        q = q.filter(models.Purchase.status == status)
    if supplier_id:
        q = q.filter(models.Purchase.supplier_id == supplier_id)
    if date_from:
        q = q.filter(models.Purchase.date >= date_from)
    if date_to:
        q = q.filter(models.Purchase.date <= date_to)
    return paginate(q, page, per_page)


def create_purchase(db: Session, obj: schemas.PurchaseCreate, number: str, created_by: int) -> models.Purchase:
    total = sum(i.quantity * i.price for i in obj.items)
    db_obj = models.Purchase(
        number=number,
        supplier_id=obj.supplier_id,
        date=obj.date or func.now(),
        total_amount=total,
        status=models.DocumentStatus.draft,
        comment=obj.comment,
        created_by=created_by,
    )
    db.add(db_obj)
    db.flush()
    for item in obj.items:
        pi = models.PurchaseItem(
            purchase_id=db_obj.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            amount=item.quantity * item.price,
        )
        db.add(pi)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_purchase(db: Session, db_obj: models.Purchase, obj: schemas.PurchaseUpdate) -> models.Purchase:
    if db_obj.status != models.DocumentStatus.draft:
        raise ValueError("Редактировать можно только черновик")
    if obj.supplier_id is not None:
        db_obj.supplier_id = obj.supplier_id
    if obj.date is not None:
        db_obj.date = obj.date
    if obj.comment is not None:
        db_obj.comment = obj.comment
    if obj.items is not None:
        # Удаляем старые строки
        for old in db_obj.items:
            db.delete(old)
        db.flush()
        total = 0
        for item in obj.items:
            pi = models.PurchaseItem(
                purchase_id=db_obj.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                amount=item.quantity * item.price,
            )
            db.add(pi)
            total += item.quantity * item.price
        db_obj.total_amount = total
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_purchase(db: Session, db_obj: models.Purchase) -> None:
    if db_obj.status != models.DocumentStatus.draft:
        raise ValueError("Удалять можно только черновик")
    db.delete(db_obj)
    db.commit()


# ============================
# Sales
# ============================
def get_sale(db: Session, sale_id: int) -> Optional[models.Sale]:
    return db.query(models.Sale).filter(models.Sale.id == sale_id).first()


def get_sales(db: Session, page: int = 1, per_page: int = 10, status: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None, client_id: Optional[int] = None):
    q = db.query(models.Sale).order_by(models.Sale.id.desc())
    if status:
        q = q.filter(models.Sale.status == status)
    if client_id:
        q = q.filter(models.Sale.client_id == client_id)
    if date_from:
        q = q.filter(models.Sale.date >= date_from)
    if date_to:
        q = q.filter(models.Sale.date <= date_to)
    return paginate(q, page, per_page)


def create_sale(db: Session, obj: schemas.SaleCreate, number: str, created_by: int) -> models.Sale:
    total = sum(i.quantity * i.price for i in obj.items)
    db_obj = models.Sale(
        number=number,
        client_id=obj.client_id,
        date=obj.date or func.now(),
        total_amount=total,
        total_cost=0,
        status=models.DocumentStatus.draft,
        comment=obj.comment,
        created_by=created_by,
    )
    db.add(db_obj)
    db.flush()
    for item in obj.items:
        si = models.SaleItem(
            sale_id=db_obj.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            amount=item.quantity * item.price,
            cost=0,
        )
        db.add(si)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_sale(db: Session, db_obj: models.Sale, obj: schemas.SaleUpdate) -> models.Sale:
    if db_obj.status != models.DocumentStatus.draft:
        raise ValueError("Редактировать можно только черновик")
    if obj.client_id is not None:
        db_obj.client_id = obj.client_id
    if obj.date is not None:
        db_obj.date = obj.date
    if obj.comment is not None:
        db_obj.comment = obj.comment
    if obj.items is not None:
        for old in db_obj.items:
            db.delete(old)
        db.flush()
        total = 0
        for item in obj.items:
            si = models.SaleItem(
                sale_id=db_obj.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                amount=item.quantity * item.price,
                cost=0,
            )
            db.add(si)
            total += item.quantity * item.price
        db_obj.total_amount = total
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_sale(db: Session, db_obj: models.Sale) -> None:
    if db_obj.status != models.DocumentStatus.draft:
        raise ValueError("Удалять можно только черновик")
    db.delete(db_obj)
    db.commit()


# ============================
# Settings
# ============================
def get_setting(db: Session, key: str) -> Optional[models.Setting]:
    return db.query(models.Setting).filter(models.Setting.key == key).first()


def set_setting(db: Session, key: str, value: str) -> models.Setting:
    s = get_setting(db, key)
    if s:
        s.value = value
    else:
        s = models.Setting(key=key, value=value)
        db.add(s)
    db.commit()
    db.refresh(s)
    return s


def get_company_settings(db: Session) -> schemas.CompanySettings:
    keys = ["company_name", "company_inn", "company_kpp", "company_address", "company_phone", "company_email", "default_min_stock", "db_url"]
    result = {}
    for k in keys:
        s = get_setting(db, k)
        if s:
            result[k] = s.value
        else:
            result[k] = None
    return schemas.CompanySettings(
        company_name=result.get("company_name"),
        company_inn=result.get("company_inn"),
        company_kpp=result.get("company_kpp"),
        company_address=result.get("company_address"),
        company_phone=result.get("company_phone"),
        company_email=result.get("company_email"),
        default_min_stock=float(result.get("default_min_stock") or 0),
        db_url=result.get("db_url"),
    )


def save_company_settings(db: Session, data: schemas.CompanySettings) -> schemas.CompanySettings:
    mapping = data.model_dump()
    for k, v in mapping.items():
        if v is not None:
            set_setting(db, k, str(v))
    return get_company_settings(db)
