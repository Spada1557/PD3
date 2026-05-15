from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
from decimal import Decimal


def round_float(v):
    return round(v, 2) if v is not None else None


class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    data: list


class ErrorResponse(BaseModel):
    error: str
    message: str


# ─── AUTH ────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


# ─── USERS ───────────────────────────────────────────────────────
class UserCreate(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="manager", pattern="^(admin|manager|warehouse)$")
    status: str = Field(default="active", pattern="^(active|inactive)$")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|manager|warehouse)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ─── CATEGORIES ──────────────────────────────────────────────────
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ─── UNITS ───────────────────────────────────────────────────────
class UnitCreate(BaseModel):
    name: str = Field(..., max_length=50)
    short_name: str = Field(..., max_length=10)


class UnitUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    short_name: Optional[str] = Field(None, max_length=10)


class UnitResponse(BaseModel):
    id: int
    name: str
    short_name: str

    class Config:
        from_attributes = True


# ─── WAREHOUSES ──────────────────────────────────────────────────
class WarehouseCreate(BaseModel):
    name: str = Field(..., max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class WarehouseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class WarehouseResponse(BaseModel):
    id: int
    name: str
    address: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# ─── PRODUCTS ────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    article: str = Field(..., min_length=2, max_length=20, pattern=r"^[A-Za-z0-9\-]+$")
    category_id: int
    unit_id: int
    price: float = Field(..., ge=0)
    cost: float = Field(..., ge=0)
    min_stock: float = Field(default=10.0, ge=0)
    status: str = Field(default="active")
    description: Optional[str] = Field(None, max_length=1000)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    article: Optional[str] = Field(None, min_length=2, max_length=20, pattern=r"^[A-Za-z0-9\-]+$")
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    price: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    min_stock: Optional[float] = Field(None, ge=0)
    status: Optional[str] = None
    description: Optional[str] = Field(None, max_length=1000)


class ProductResponse(BaseModel):
    id: int
    name: str
    article: str
    category_id: int
    unit_id: int
    price: float
    cost: float
    min_stock: float
    status: str
    image_path: Optional[str] = None
    description: Optional[str] = None
    category: Optional[CategoryResponse] = None
    unit: Optional[UnitResponse] = None

    class Config:
        from_attributes = True


# ─── SUPPLIERS ───────────────────────────────────────────────────
class SupplierCreate(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    kpp: Optional[str] = Field(None, max_length=9)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active")


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    kpp: Optional[str] = Field(None, max_length=9)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str] = None
    kpp: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ─── CLIENTS ─────────────────────────────────────────────────────
class ClientCreate(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    status: str = Field(default="active")


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    contact_person: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = None


class ClientResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


# ─── PURCHASE ITEMS ──────────────────────────────────────────────
class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    amount: float = Field(..., ge=0)


class PurchaseItemResponse(BaseModel):
    id: int
    purchase_id: int
    product_id: int
    quantity: float
    price: float
    amount: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# ─── PURCHASES ───────────────────────────────────────────────────
class PurchaseCreate(BaseModel):
    supplier_id: int
    date: datetime
    comment: Optional[str] = Field(None, max_length=1000)
    items: list[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    items: Optional[list[PurchaseItemCreate]] = None


class PurchaseResponse(BaseModel):
    id: int
    number: str
    supplier_id: int
    date: datetime
    total_amount: float
    status: str
    comment: Optional[str] = None
    created_by: int
    supplier: Optional[SupplierResponse] = None
    items: list[PurchaseItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ─── SALE ITEMS ──────────────────────────────────────────────────
class SaleItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(..., ge=0)
    amount: float = Field(..., ge=0)


class SaleItemResponse(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: float
    price: float
    amount: float
    cost: float
    product: Optional[ProductResponse] = None

    class Config:
        from_attributes = True


# ─── SALES ───────────────────────────────────────────────────────
class SaleCreate(BaseModel):
    client_id: int
    date: datetime
    comment: Optional[str] = Field(None, max_length=1000)
    items: list[SaleItemCreate]


class SaleUpdate(BaseModel):
    client_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    items: Optional[list[SaleItemCreate]] = None


class SaleResponse(BaseModel):
    id: int
    number: str
    client_id: int
    date: datetime
    total_amount: float
    total_cost: float
    total_profit: float
    status: str
    comment: Optional[str] = None
    created_by: int
    client: Optional[ClientResponse] = None
    items: list[SaleItemResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# ─── STOCK ───────────────────────────────────────────────────────
class StockResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: float
    reserved: float
    avg_cost: float
    available: Optional[float] = None
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None

    class Config:
        from_attributes = True


class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    type: str
    quantity: float
    direction: str
    document_type: Optional[str] = None
    document_id: Optional[int] = None
    created_by: int
    comment: Optional[str] = None
    created_at: datetime
    product: Optional[ProductResponse] = None
    warehouse: Optional[WarehouseResponse] = None
    created_by_user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class InventoryItem(BaseModel):
    product_id: int
    fact_quantity: float = Field(..., ge=0)


class InventoryRequest(BaseModel):
    warehouse_id: int
    items: list[InventoryItem]


class StockTransferRequest(BaseModel):
    product_id: int
    from_warehouse_id: int
    to_warehouse_id: int
    quantity: float = Field(..., gt=0)


# ─── NOTIFICATIONS ───────────────────────────────────────────────
class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    is_read: bool
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── DASHBOARD ──────────────────────────────────────────────────
class DashboardResponse(BaseModel):
    revenue: float
    revenue_change: float
    cost: float
    cost_change: float
    profit: float
    profit_change: float
    stock_count: int
    stock_value: float
    orders_count: int
    orders_change: float
    sales_chart: list[dict]
    category_distribution: list[dict]
    top_products: list[dict]
    top_documents: list[dict]
    low_stock: list[dict]


# ─── REPORTS ─────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    category_id: Optional[int] = None
    product_id: Optional[int] = None


# ─── SETTINGS ────────────────────────────────────────────────────
class SettingsItemResponse(BaseModel):
    id: int
    key: str
    value: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class SettingsUpdateRequest(BaseModel):
    key: str
    value: str


class DatabaseConfigRequest(BaseModel):
    database_url: str
