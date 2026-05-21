import re
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: str = Field(default="manager")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("admin", "manager", "warehouse"):
            raise ValueError("Role must be admin, manager, or warehouse")
        return v


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v is not None and v not in ("admin", "manager", "warehouse"):
            raise ValueError("Role must be admin, manager, or warehouse")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("active", "inactive"):
            raise ValueError("Status must be active or inactive")
        return v


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UnitCreate(BaseModel):
    name: str = Field(..., max_length=50)
    short_name: str = Field(..., max_length=10)


class UnitOut(BaseModel):
    id: int
    name: str
    short_name: str

    class Config:
        from_attributes = True


class WarehouseCreate(BaseModel):
    name: str = Field(..., max_length=255)
    address: Optional[str] = None
    is_active: bool = True


class WarehouseOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=255)
    article: str = Field(..., min_length=2, max_length=20)
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    price: float = Field(..., ge=0)
    cost: float = Field(0, ge=0)
    min_stock: int = Field(10, ge=0)
    status: str = Field(default="active")
    image_path: Optional[str] = None

    @field_validator("article")
    @classmethod
    def validate_article(cls, v):
        if not re.match(r"^[a-zA-Z0-9\-]{2,20}$", v):
            raise ValueError("Article must contain only latin letters, digits, and hyphens (2-20 chars)")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    article: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    price: Optional[float] = Field(None, ge=0)
    cost: Optional[float] = Field(None, ge=0)
    min_stock: Optional[int] = Field(None, ge=0)
    status: Optional[str] = None
    image_path: Optional[str] = None

    @field_validator("article")
    @classmethod
    def validate_article(cls, v):
        if v is not None and not re.match(r"^[a-zA-Z0-9\-]{2,20}$", v):
            raise ValueError("Article must contain only latin letters, digits, and hyphens (2-20 chars)")
        return v


class ProductOut(BaseModel):
    id: int
    name: str
    article: str
    category_id: Optional[int]
    unit_id: Optional[int]
    price: float
    cost: float
    min_stock: int
    status: str
    image_path: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SupplierCreate(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    kpp: Optional[str] = Field(None, max_length=9)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=1000)


class SupplierOut(BaseModel):
    id: int
    name: str
    inn: Optional[str]
    kpp: Optional[str]
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    comment: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=1000)


class ClientOut(BaseModel):
    id: int
    name: str
    inn: Optional[str]
    contact_person: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    comment: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StockOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity: float
    reserved: float
    avg_cost: float
    available: float = 0.0
    product_name: Optional[str] = None
    warehouse_name: Optional[str] = None

    class Config:
        from_attributes = True


class StockMovementOut(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    type: str
    quantity: float
    direction: int
    document_type: Optional[str]
    document_id: Optional[int]
    comment: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(0, ge=0)


class PurchaseItemOut(BaseModel):
    id: int
    purchase_id: int
    product_id: int
    quantity: float
    price: float
    amount: float
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class PurchaseCreate(BaseModel):
    supplier_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    items: List[PurchaseItemCreate]


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    items: Optional[List[PurchaseItemCreate]] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("draft", "posted", "cancelled"):
            raise ValueError("Invalid status")
        return v


class PurchaseOut(BaseModel):
    id: int
    number: str
    supplier_id: Optional[int]
    date: datetime
    total_amount: float
    status: str
    comment: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    items: List[PurchaseItemOut] = []
    supplier_name: Optional[str] = None

    class Config:
        from_attributes = True


class SaleItemCreate(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(0, ge=0)


class SaleItemOut(BaseModel):
    id: int
    sale_id: int
    product_id: int
    quantity: float
    price: float
    amount: float
    cost: float
    profit: float
    product_name: Optional[str] = None

    class Config:
        from_attributes = True


class SaleCreate(BaseModel):
    client_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    items: List[SaleItemCreate]


class SaleUpdate(BaseModel):
    client_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = None
    items: Optional[List[SaleItemCreate]] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ("draft", "posted", "cancelled"):
            raise ValueError("Invalid status")
        return v


class SaleOut(BaseModel):
    id: int
    number: str
    client_id: Optional[int]
    date: datetime
    total_amount: float
    cost_amount: float
    profit_amount: float
    status: str
    comment: Optional[str]
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    items: List[SaleItemOut] = []
    client_name: Optional[str] = None

    class Config:
        from_attributes = True


class NotificationOut(BaseModel):
    id: int
    user_id: Optional[int]
    type: str
    title: str
    message: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AppSettingsUpdate(BaseModel):
    company_name: Optional[str] = None
    company_inn: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    min_stock_default: Optional[int] = Field(None, ge=0)
    db_connection_string: Optional[str] = None


class AppSettingsOut(BaseModel):
    id: int
    company_name: str
    company_inn: Optional[str]
    company_address: Optional[str]
    company_phone: Optional[str]
    min_stock_default: int
    db_connection_string: str
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    data: List


class DashboardStats(BaseModel):
    revenue: float = 0.0
    cost: float = 0.0
    profit: float = 0.0
    stock_value: float = 0.0
    orders_count: int = 0
    revenue_change: float = 0.0
    cost_change: float = 0.0
    profit_change: float = 0.0
    stock_change: float = 0.0


class DashboardSalesChart(BaseModel):
    labels: List[str] = []
    revenue: List[float] = []
    cost: List[float] = []
    profit: List[float] = []


class DashboardCategoryChart(BaseModel):
    labels: List[str] = []
    values: List[float] = []


class TopProduct(BaseModel):
    id: int
    name: str
    article: str
    value: float
    quantity: float = 0.0


class LowStockProduct(BaseModel):
    id: int
    name: str
    article: str
    quantity: float
    min_stock: int


class ErrorResponse(BaseModel):
    error: str
    message: str