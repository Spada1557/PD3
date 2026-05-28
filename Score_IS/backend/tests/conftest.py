import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app import models, crud

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def seeded_db(db):
    """БД с минимальным набором данных: пользователь, склад, товар."""
    import bcrypt

    pwd = bcrypt.hashpw(b"pass", bcrypt.gensalt()).decode()
    user = models.User(
        name="Test",
        email="test@test.com",
        password_hash=pwd,
        role=models.UserRole.admin,
        status=models.UserStatus.active,
    )
    db.add(user)

    category = models.Category(name="Тест")
    unit = models.Unit(name="шт")
    db.add_all([category, unit])
    db.flush()

    product = models.Product(
        name="Кастрюля",
        article="TEST-001",
        category_id=category.id,
        unit_id=unit.id,
        price=500.0,
        cost=300.0,
        min_stock=0.0,
    )
    db.add(product)

    warehouse = models.Warehouse(name="Основной", is_default=1)
    db.add(warehouse)
    db.commit()
    db.refresh(user)
    db.refresh(product)
    db.refresh(warehouse)

    return {"db": db, "user": user, "product": product, "warehouse": warehouse}
