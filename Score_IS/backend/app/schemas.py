from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class ErrorResponse(BaseModel):
    error: str
    message: str


# ============================
# Auth / User
# ============================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    role: str = Field(..., pattern=r"^(admin|manager|warehouse)$")
    status: str = Field(default="active", pattern=r"^(active|inactive)$")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Имя обязательно")
        return v.strip()


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================
# References
# ============================
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=255)


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True


class UnitBase(BaseModel):
    name: str = Field(..., max_length=50)


class UnitCreate(UnitBase):
    pass


class UnitOut(UnitBase):
    id: int

    class Config:
        from_attributes = True


class WarehouseBase(BaseModel):
    name: str = Field(..., max_length=255)
    is_default: int = 0


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseOut(WarehouseBase):
    id: int

    class Config:
        from_attributes = True


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    kpp: Optional[str] = Field(None, max_length=9)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=1000)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    name: str = Field(..., max_length=255)
    inn: Optional[str] = Field(None, max_length=12)
    contact_phone: Optional[str] = Field(None, max_length=50)
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=1000)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientOut(ClientBase):
    id: int

    class Config:
        from_attributes = True


# ============================
# Product
# ============================
class ProductBase(BaseModel):
    name: str = Field(..., max_length=255)
    article: str = Field(..., min_length=2, max_length=20)
    category_id: int
    unit_id: int
    price: float = Field(default=0.0, ge=0)
    cost: float = Field(default=0.0, ge=0)
    min_stock: float = Field(default=0.0, ge=0)
    status: str = Field(default="active", max_length=20)

    @field_validator("article")
    @classmethod
    def article_alphanumeric(cls, v):
        if not re.fullmatch(r"[A-Za-z0-9\-]{2,20}", v):
            raise ValueError("Артикул: латиница, цифры, дефис, 2–20 симв.")
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    article: Optional[str] = None
    category_id: Optional[int] = None
    unit_id: Optional[int] = None
    price: Optional[float] = None
    cost: Optional[float] = None
    min_stock: Optional[float] = None
    status: Optional[str] = None
    image_path: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    image_path: Optional[str] = None
    created_at: Optional[datetime] = None
    category: Optional[CategoryOut] = None
    unit: Optional[UnitOut] = None

    class Config:
        from_attributes = True


# ============================
# Stock
# ============================
class StockBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: float = Field(default=0.0, ge=0)
    reserved: float = Field(default=0.0, ge=0)
    avg_cost: float = Field(default=0.0, ge=0)


class StockOut(StockBase):
    id: int
    product: Optional[ProductOut] = None
    warehouse: Optional[WarehouseOut] = None
    available: float = 0.0

    class Config:
        from_attributes = True


class StockMovementBase(BaseModel):
    product_id: int
    warehouse_id: int
    type: str
    quantity: float = Field(..., gt=0)
    direction: int
    document_type: str
    document_id: int


class StockMovementOut(StockMovementBase):
    id: int
    created_by: int
    created_at: datetime
    product: Optional[ProductOut] = None
    warehouse: Optional[WarehouseOut] = None
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True


class InventoryItem(BaseModel):
    product_id: int
    warehouse_id: int
    fact_quantity: float = Field(..., ge=0)


# ============================
# Purchase / PurchaseItem
# ============================
class PurchaseItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(..., ge=0)


class PurchaseItemCreate(PurchaseItemBase):
    pass


class PurchaseItemOut(PurchaseItemBase):
    id: int
    amount: float
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True


class PurchaseBase(BaseModel):
    supplier_id: int
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)


class PurchaseCreate(PurchaseBase):
    items: List[PurchaseItemCreate] = Field(..., min_length=1)


class PurchaseUpdate(BaseModel):
    supplier_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = None
    items: Optional[List[PurchaseItemCreate]] = None


class PurchaseOut(PurchaseBase):
    id: int
    number: str
    total_amount: float
    status: str
    created_by: int
    created_at: datetime
    supplier: Optional[SupplierOut] = None
    items: List[PurchaseItemOut] = []
    created_by_user: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ============================
# Sale / SaleItem
# ============================
class SaleItemBase(BaseModel):
    product_id: int
    quantity: float = Field(..., gt=0)
    price: float = Field(..., ge=0)


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemOut(SaleItemBase):
    id: int
    amount: float
    cost: float
    product: Optional[ProductOut] = None

    class Config:
        from_attributes = True


class SaleBase(BaseModel):
    client_id: int
    date: Optional[datetime] = None
    comment: Optional[str] = Field(None, max_length=1000)


class SaleCreate(SaleBase):
    items: List[SaleItemCreate] = Field(..., min_length=1)


class SaleUpdate(BaseModel):
    client_id: Optional[int] = None
    date: Optional[datetime] = None
    comment: Optional[str] = None
    items: Optional[List[SaleItemCreate]] = None


class SaleOut(SaleBase):
    id: int
    number: str
    total_amount: float
    total_cost: float
    status: str
    created_by: int
    created_at: datetime
    client: Optional[ClientOut] = None
    items: List[SaleItemOut] = []
    created_by_user: Optional[UserOut] = None

    class Config:
        from_attributes = True


# ============================
# Settings
# ============================
class SettingBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: str


class SettingCreate(SettingBase):
    pass


class SettingOut(SettingBase):
    id: int

    class Config:
        from_attributes = True


class CompanySettings(BaseModel):
    company_name: Optional[str] = None
    company_inn: Optional[str] = None
    company_kpp: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_email: Optional[str] = None
    default_min_stock: float = 0.0
    db_url: Optional[str] = None


# ============================
# Pagination
# ============================
class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    data: list


# ============================
# Dashboard
# ============================
class DashboardSummary(BaseModel):
    revenue: float
    cost: float
    profit: float
    stock_value: float
    orders_count: int
    revenue_change_percent: float
    profit_change_percent: float


class DashboardSalePoint(BaseModel):
    date: str
    revenue: float
    cost: float
    profit: float


class DashboardCategorySlice(BaseModel):
    category: str
    revenue: float


class TopProduct(BaseModel):
    product_id: int
    name: str
    article: str
    revenue: float
    quantity: float


class TopDocument(BaseModel):
    document_id: int
    number: str
    total_amount: float
    date: str


class LowStockItem(BaseModel):
    product_id: int
    name: str
    article: str
    quantity: float
    min_stock: float


class DashboardData(BaseModel):
    summary: DashboardSummary
    sales_chart: List[DashboardSalePoint]
    categories_chart: List[DashboardCategorySlice]
    top_products: List[TopProduct]
    top_documents: List[TopDocument]
    low_stock: List[LowStockItem]


class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

