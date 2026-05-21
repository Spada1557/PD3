from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole, UserStatus, Warehouse, Category, Unit, Product, Stock
from app.utils.security import hash_password


def seed_data():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        admin = User(
            name="Администратор",
            email="admin@enamelpro.local",
            password_hash=hash_password("admin123"),
            role=UserRole.admin,
            status=UserStatus.active,
        )
        manager = User(
            name="Менеджер Иванов",
            email="manager@enamelpro.local",
            password_hash=hash_password("manager123"),
            role=UserRole.manager,
            status=UserStatus.active,
        )
        warehouse = User(
            name="Кладовщик Петров",
            email="warehouse@enamelpro.local",
            password_hash=hash_password("warehouse123"),
            role=UserRole.warehouse,
            status=UserStatus.active,
        )
        db.add_all([admin, manager, warehouse])
        db.flush()

        wh_main = Warehouse(name="Основной склад", address="г. Москва, ул. Промышленная, 1")
        wh_reserve = Warehouse(name="Резервный склад", address="г. Москва, ул. Запасная, 5")
        db.add_all([wh_main, wh_reserve])
        db.flush()

        categories = [
            Category(name="Кастрюли", description="Эмалированные кастрюли"),
            Category(name="Миски", description="Эмалированные миски"),
            Category(name="Тазы", description="Эмалированные тазы"),
            Category(name="Кружки", description="Эмалированные кружки"),
            Category(name="Вёдра", description="Эмалированные вёдра"),
        ]
        db.add_all(categories)
        db.flush()

        units = [
            Unit(name="Штука", short_name="шт"),
            Unit(name="Килограмм", short_name="кг"),
            Unit(name="Комплект", short_name="компл"),
        ]
        db.add_all(units)
        db.flush()

        products_data = [
            {"name": "Кастрюля 2л", "article": "KAS-001", "category_id": 1, "unit_id": 1, "price": 850.0, "cost": 450.0, "min_stock": 20.0},
            {"name": "Кастрюля 3л", "article": "KAS-002", "category_id": 1, "unit_id": 1, "price": 1100.0, "cost": 580.0, "min_stock": 15.0},
            {"name": "Кастрюля 5л", "article": "KAS-003", "category_id": 1, "unit_id": 1, "price": 1600.0, "cost": 780.0, "min_stock": 10.0},
            {"name": "Миска 1.5л", "article": "MSK-001", "category_id": 2, "unit_id": 1, "price": 420.0, "cost": 200.0, "min_stock": 30.0},
            {"name": "Миска 3л", "article": "MSK-002", "category_id": 2, "unit_id": 1, "price": 650.0, "cost": 320.0, "min_stock": 25.0},
            {"name": "Таз 10л", "article": "TAZ-001", "category_id": 3, "unit_id": 1, "price": 950.0, "cost": 480.0, "min_stock": 15.0},
            {"name": "Таз 15л", "article": "TAZ-002", "category_id": 3, "unit_id": 1, "price": 1200.0, "cost": 600.0, "min_stock": 10.0},
            {"name": "Кружка 0.5л", "article": "KRG-001", "category_id": 4, "unit_id": 1, "price": 280.0, "cost": 120.0, "min_stock": 50.0},
            {"name": "Ведро 8л", "article": "VED-001", "category_id": 5, "unit_id": 1, "price": 750.0, "cost": 380.0, "min_stock": 20.0},
            {"name": "Ведро 12л", "article": "VED-002", "category_id": 5, "unit_id": 1, "price": 980.0, "cost": 490.0, "min_stock": 15.0},
        ]
        for p in products_data:
            product = Product(**p)
            db.add(product)
            db.flush()
            stock = Stock(
                product_id=product.id,
                warehouse_id=wh_main.id,
                quantity=round(p["min_stock"] * 3),
                reserved=0.0,
                avg_cost=p["cost"],
            )
            db.add(stock)

        from app.models import Supplier, Client
        supplier = Supplier(
            name="ООО МеталлСнаб",
            inn="7701234567",
            kpp="770101001",
            contact_person="Сидоров А.В.",
            phone="+7-495-123-45-67",
            email="info@metallsnab.ru",
            address="г. Москва, ул. Металлургов, 10",
        )
        client1 = Client(
            name="ООО ХозТорг",
            inn="7707654321",
            contact_person="Алексеев П.С.",
            phone="+7-495-765-43-21",
            email="info@hoztorg.ru",
            address="г. Москва, ул. Торговая, 20",
        )
        client2 = Client(
            name="ИП Кузнецов",
            inn="771234567890",
            contact_person="Кузнецов Д.И.",
            phone="+7-926-111-22-33",
            email="kuznetsov@mail.ru",
            address="г. Москва, ул. Дачная, 5",
        )
        db.add_all([supplier, client1, client2])

        from app.models import Settings
        db_settings = [
            Settings(key="company_name", value="ООО ЭмальПром", description="Наименование предприятия"),
            Settings(key="company_inn", value="7700123456", description="ИНН предприятия"),
            Settings(key="company_kpp", value="770101001", description="КПП предприятия"),
            Settings(key="company_address", value="г. Москва, ул. Заводская, 15", description="Юридический адрес"),
            Settings(key="company_phone", value="+7-495-999-88-77", description="Телефон"),
            Settings(key="company_email", value="info@enamelpro.ru", description="Email"),
            Settings(key="default_min_stock", value="10", description="Порог min_stock по умолчанию"),
        ]
        db.add_all(db_settings)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
