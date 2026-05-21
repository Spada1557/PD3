import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum, event, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    warehouse = "warehouse"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class DocumentStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"
    cancelled = "cancelled"


class StockMovementType(str, enum.Enum):
    in_ = "in"
    out = "out"
    move = "move"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.warehouse, nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.active, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    purchases = relationship("Purchase", back_populates="created_by_user")
    sales = relationship("Sale", back_populates="created_by_user")


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)

    products = relationship("Product", back_populates="category")


class Unit(Base):
    __tablename__ = "units"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)

    products = relationship("Product", back_populates="unit")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    is_default = Column(Integer, default=0)

    stocks = relationship("Stock", back_populates="warehouse")


class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(12))
    kpp = Column(String(9))
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    address = Column(Text)

    purchases = relationship("Purchase", back_populates="supplier")


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(12))
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    address = Column(Text)

    sales = relationship("Sale", back_populates="client")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    article = Column(String(20), unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)
    min_stock = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="active")
    image_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    stock_items = relationship("Stock", back_populates="product")


class Stock(Base):
    __tablename__ = "stock"
    __table_args__ = (UniqueConstraint("product_id", "warehouse_id", name="uix_stock_product_warehouse"),)
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    reserved = Column(Float, default=0.0, nullable=False)
    avg_cost = Column(Float, default=0.0, nullable=False)

    product = relationship("Product", back_populates="stock_items")
    warehouse = relationship("Warehouse", back_populates="stocks")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    type = Column(Enum(StockMovementType), nullable=False)
    quantity = Column(Float, nullable=False)
    direction = Column(Integer, nullable=False)  # +1 или -1
    document_type = Column(String(20), nullable=False)
    document_id = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")
    warehouse = relationship("Warehouse")
    user = relationship("User")


class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.draft, nullable=False)
    comment = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    supplier = relationship("Supplier", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")
    created_by_user = relationship("User", back_populates="purchases")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"
    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product")


class Sale(Base):
    __tablename__ = "sales"
    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    total_amount = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.draft, nullable=False)
    comment = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    created_by_user = relationship("User", back_populates="sales")


class SaleItem(Base):
    __tablename__ = "sale_items"
    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    cost = Column(Float, default=0.0, nullable=False)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product")


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=False)
