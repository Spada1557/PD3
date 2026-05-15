import os, bcrypt
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, User, UserRole, UserStatus, Category, Unit, Warehouse, Supplier, Client, Product, Stock

Base.metadata.create_all(bind=engine)

db: Session = SessionLocal()

# Admin
if not db.query(User).filter(User.email == "admin@example.com").first():
    pwd = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
    db.add(User(name="Администратор", email="admin@example.com", password_hash=pwd, role=UserRole.admin, status=UserStatus.active))
    db.commit()

# Categories
for name in ["Кастрюли", "Миски", "Тазы", "Кружки", "Сковороды"]:
    if not db.query(Category).filter(Category.name == name).first():
        db.add(Category(name=name))

# Units
for name in ["шт", "кг", "л", "компл"]:
    if not db.query(Unit).filter(Unit.name == name).first():
        db.add(Unit(name=name))

# Warehouses
for name, is_default in [("Основной", 1), ("Резерв", 0)]:
    if not db.query(Warehouse).filter(Warehouse.name == name).first():
        db.add(Warehouse(name=name, is_default=is_default))

# Suppliers
for data in [
    {"name": "ООО Посуда-Трейд", "inn": "1234567890", "contact_phone": "+7 900 111-22-33"},
    {"name": "ИП Иванов", "inn": "9876543210", "contact_phone": "+7 900 444-55-66"},
]:
    if not db.query(Supplier).filter(Supplier.name == data["name"]).first():
        db.add(Supplier(**data))

# Clients
for data in [
    {"name": "ООО Торг", "inn": "1122334455", "contact_phone": "+7 800 100-20-30"},
    {"name": "ИП Петров", "inn": "5544332211", "contact_phone": "+7 800 400-50-60"},
]:
    if not db.query(Client).filter(Client.name == data["name"]).first():
        db.add(Client(**data))

db.commit()

# Products
unit = db.query(Unit).filter(Unit.name == "шт").first()
cat = db.query(Category).filter(Category.name == "Кастрюли").first()
wh = db.query(Warehouse).filter(Warehouse.name == "Основной").first()

for article, name, price, cost, min_stock in [
    ("KAS-001", "Кастрюля эмалированная 3л", 650.0, 420.0, 10.0),
    ("KAS-002", "Кастрюля эмалированная 5л", 890.0, 580.0, 8.0),
    ("MIS-001", "Миска эмалированная 1.5л", 320.0, 210.0, 20.0),
    ("TAZ-001", "Таз эмалированный 10л", 1200.0, 780.0, 5.0),
    ("KRZ-001", "Кружка эмалированная 250мл", 180.0, 110.0, 50.0),
]:
    existing = db.query(Product).filter(Product.article == article).first()
    if not existing:
        p = Product(
            name=name,
            article=article,
            category_id=cat.id if cat else None,
            unit_id=unit.id if unit else None,
            price=price,
            cost=cost,
            min_stock=min_stock,
            status="active",
        )
        db.add(p)
        db.flush()
        if wh:
            db.add(Stock(product_id=p.id, warehouse_id=wh.id, quantity=100, reserved=0, avg_cost=cost))

db.commit()
db.close()
print("Seed done")
