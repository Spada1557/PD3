from datetime import datetime
from sqlalchemy.orm import Session
from enamelware.models import (
    User, Category, Unit, Warehouse, Supplier, Client, Product, Stock, AppSettings
)
from enamelware.auth import hash_password
from enamelware.enums import UserRole, UserStatus, ProductStatus


def seed_database(db: Session):
    if db.query(User).first():
        return

    admin = User(
        name="Администратор",
        email="admin@enamelware.ru",
        password_hash=hash_password("admin123"),
        role=UserRole.admin,
        status=UserStatus.active,
    )
    db.add(admin)

    manager = User(
        name="Менеджер",
        email="manager@enamelware.ru",
        password_hash=hash_password("manager123"),
        role=UserRole.manager,
        status=UserStatus.active,
    )
    db.add(manager)

    warehouse_user = User(
        name="Кладовщик",
        email="warehouse@enamelware.ru",
        password_hash=hash_password("warehouse123"),
        role=UserRole.warehouse,
        status=UserStatus.active,
    )
    db.add(warehouse_user)

    categories_data = [
        Category(name="Кастрюли", description="Эмалированные кастрюли"),
        Category(name="Миски", description="Эмалированные миски"),
        Category(name="Тазы", description="Эмалированные тазы"),
        Category(name="Сковороды", description="Эмалированные сковороды"),
        Category(name="Ковши", description="Эмалированные ковши и ковшики"),
    ]
    for c in categories_data:
        db.add(c)
    db.flush()

    units_data = [
        Unit(name="Штука", short_name="шт"),
        Unit(name="Набор", short_name="наб"),
    ]
    for u in units_data:
        db.add(u)
    db.flush()

    warehouses_data = [
        Warehouse(name="Основной", address="Склад 1, ул. Промышленная, д.1"),
        Warehouse(name="Резерв", address="Склад 2, ул. Запасная, д.5"),
    ]
    for w in warehouses_data:
        db.add(w)
    db.flush()

    suppliers_data = [
        Supplier(name="ООО \"МеталлСнаб\"", inn="7712345678", kpp="771201001", contact_person="Иванов И.И.", phone="+7(495)123-45-67", email="info@metallsnab.ru", address="г. Москва"),
        Supplier(name="ЗАО \"ТехноПром\"", inn="7834567890", kpp="783401001", contact_person="Петров П.П.", phone="+7(812)987-65-43", email="petrov@technoprom.ru", address="г. Санкт-Петербург"),
    ]
    for s in suppliers_data:
        db.add(s)
    db.flush()

    clients_data = [
        Client(name="ООО \"Дом посуды\"", inn="7701987654", contact_person="Сидоров С.С.", phone="+7(495)111-22-33", email="info@domposudy.ru", address="г. Москва, ул. Торговая, д.10"),
        Client(name="ИП Козлова А.В.", inn="502912345678", contact_person="Козлова А.В.", phone="+7(916)555-44-33", email="kozlova@mail.ru", address="г. Подольск"),
    ]
    for c in clients_data:
        db.add(c)
    db.flush()

    products_data = [
        Product(name="Кастрюля 2л эмаль", article="KAS-2L", category_id=categories_data[0].id, unit_id=units_data[0].id, price=850.0, cost=520.0, min_stock=10, status=ProductStatus.active),
        Product(name="Кастрюля 3л эмаль", article="KAS-3L", category_id=categories_data[0].id, unit_id=units_data[0].id, price=1100.0, cost=680.0, min_stock=10, status=ProductStatus.active),
        Product(name="Кастрюля 5л эмаль", article="KAS-5L", category_id=categories_data[0].id, unit_id=units_data[0].id, price=1500.0, cost=900.0, min_stock=8, status=ProductStatus.active),
        Product(name="Миска 1.5л эмаль", article="MIS-15", category_id=categories_data[1].id, unit_id=units_data[0].id, price=450.0, cost=280.0, min_stock=15, status=ProductStatus.active),
        Product(name="Миска 2.5л эмаль", article="MIS-25", category_id=categories_data[1].id, unit_id=units_data[0].id, price=620.0, cost=380.0, min_stock=12, status=ProductStatus.active),
        Product(name="Таз 10л эмаль", article="Taz-10", category_id=categories_data[2].id, unit_id=units_data[0].id, price=1200.0, cost=750.0, min_stock=5, status=ProductStatus.active),
        Product(name="Таз 15л эмаль", article="Taz-15", category_id=categories_data[2].id, unit_id=units_data[0].id, price=1600.0, cost=1000.0, min_stock=5, status=ProductStatus.active),
        Product(name="Сковорода 26см эмаль", article="SKV-26", category_id=categories_data[3].id, unit_id=units_data[0].id, price=950.0, cost=580.0, min_stock=10, status=ProductStatus.active),
        Product(name="Ковш 1.5л эмаль", article="KOV-15", category_id=categories_data[4].id, unit_id=units_data[0].id, price=550.0, cost=330.0, min_stock=10, status=ProductStatus.active),
        Product(name="Набор кастрюль 3шт", article="NB-K3", category_id=categories_data[0].id, unit_id=units_data[1].id, price=3500.0, cost=2100.0, min_stock=5, status=ProductStatus.active),
    ]
    for p in products_data:
        db.add(p)
    db.flush()

    for p in products_data:
        for w in warehouses_data:
            stock = Stock(product_id=p.id, warehouse_id=w.id, quantity=0, reserved=0, avg_cost=p.cost)
            db.add(stock)

    app_settings = AppSettings(
        company_name="ООО \"Эмальпосуда\"",
        company_inn="7700000000",
        company_address="г. Москва, ул. Промышленная, д.1",
        company_phone="+7(495)000-00-00",
        min_stock_default=10,
        db_connection_string="sqlite:///./enamelware.db",
    )
    db.add(app_settings)

    db.commit()