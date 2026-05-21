from enum import Enum as PyEnum


class UserRole(str, PyEnum):
    admin = "admin"
    manager = "manager"
    warehouse = "warehouse"


class UserStatus(str, PyEnum):
    active = "active"
    inactive = "inactive"


class ProductStatus(str, PyEnum):
    active = "active"
    inactive = "inactive"


class MovementType(str, PyEnum):
    incoming = "in"
    outgoing = "out"
    move = "move"


class DocumentStatus(str, PyEnum):
    draft = "draft"
    posted = "posted"
    cancelled = "cancelled"


class DocumentType(str, PyEnum):
    purchase = "purchase"
    sale = "sale"
    inventory = "inventory"
    transfer = "transfer"