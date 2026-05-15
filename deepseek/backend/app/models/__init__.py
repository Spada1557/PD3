from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    warehouse = "warehouse"


class UserStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"


class StockMovementType(str, enum.Enum):
    in_ = "in"
    out = "out"
    move = "move"


class DocumentStatus(str, enum.Enum):
    draft = "draft"
    posted = "posted"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.manager)
    status = Column(SAEnum(UserStatus), nullable=False, default=UserStatus.active)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    stock_movements = relationship("StockMovement", back_populates="created_by_user")
    purchases = relationship("Purchase", back_populates="created_by_user")
    sales = relationship("Sale", back_populates="created_by_user")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship("Product", back_populates="category")


class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)
    short_name = Column(String(10), nullable=False)

    products = relationship("Product", back_populates="unit")


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    address = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    stocks = relationship("Stock", back_populates="warehouse")
    stock_movements = relationship("StockMovement", back_populates="warehouse")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    article = Column(String(20), unique=True, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="RESTRICT"))
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="RESTRICT"))
    price = Column(Float, nullable=False, default=0.0)
    cost = Column(Float, nullable=False, default=0.0)
    min_stock = Column(Float, nullable=False, default=10.0)
    status = Column(String(20), default="active")
    image_path = Column(String(500))
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    unit = relationship("Unit", back_populates="products")
    stock = relationship("Stock", back_populates="product")
    stock_movements = relationship("StockMovement", back_populates="product")
    purchase_items = relationship("PurchaseItem", back_populates="product")
    sale_items = relationship("SaleItem", back_populates="product")


class Stock(Base):
    __tablename__ = "stock"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Float, nullable=False, default=0.0)
    reserved = Column(Float, nullable=False, default=0.0)
    avg_cost = Column(Float, nullable=False, default=0.0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint('product_id', 'warehouse_id', name='uq_stock_product_warehouse'),)

    product = relationship("Product", back_populates="stock")
    warehouse = relationship("Warehouse", back_populates="stocks")


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="RESTRICT"), nullable=False)
    type = Column(SAEnum(StockMovementType), nullable=False)
    quantity = Column(Float, nullable=False)
    direction = Column(String(5), nullable=False)
    document_type = Column(String(50))
    document_id = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    product = relationship("Product", back_populates="stock_movements")
    warehouse = relationship("Warehouse", back_populates="stock_movements")
    created_by_user = relationship("User", back_populates="stock_movements")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(12))
    kpp = Column(String(9))
    contact_person = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())

    purchases = relationship("Purchase", back_populates="supplier")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="RESTRICT"), nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    total_amount = Column(Float, nullable=False, default=0.0)
    status = Column(SAEnum(DocumentStatus), nullable=False, default=DocumentStatus.draft)
    comment = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    supplier = relationship("Supplier", back_populates="purchases")
    created_by_user = relationship("User", back_populates="purchases")
    items = relationship("PurchaseItem", back_populates="purchase", cascade="all, delete-orphan")


class PurchaseItem(Base):
    __tablename__ = "purchase_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, ForeignKey("purchases.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)

    purchase = relationship("Purchase", back_populates="items")
    product = relationship("Product", back_populates="purchase_items")


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    inn = Column(String(12))
    contact_person = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    address = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=func.now())

    sales = relationship("Sale", back_populates="client")


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id", ondelete="RESTRICT"), nullable=False)
    date = Column(DateTime, nullable=False, server_default=func.now())
    total_amount = Column(Float, nullable=False, default=0.0)
    total_cost = Column(Float, nullable=False, default=0.0)
    total_profit = Column(Float, nullable=False, default=0.0)
    status = Column(SAEnum(DocumentStatus), nullable=False, default=DocumentStatus.draft)
    comment = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    client = relationship("Client", back_populates="sales")
    created_by_user = relationship("User", back_populates="sales")
    items = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")


class SaleItem(Base):
    __tablename__ = "sale_items"

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="RESTRICT"), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    cost = Column(Float, nullable=False, default=0.0)

    sale = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    reference_type = Column(String(50))
    reference_id = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())


class Settings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(500))
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
