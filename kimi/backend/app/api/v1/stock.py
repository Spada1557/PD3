from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app.services.document_service import inventory_adjust, move_stock
from app import crud, schemas, models

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("", response_model=schemas.PaginatedResponse)
def list_stock(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    warehouse_id: int | None = None,
    product_id: int | None = None,
    db: Session = Depends(get_db),
):
    result = crud.get_stock(db, page=page, per_page=per_page, warehouse_id=warehouse_id, product_id=product_id)
    # Явная сериализация через Pydantic для корректной подгрузки связей
    data = []
    for item in result["data"]:
        item.available = item.quantity - item.reserved
        data.append(schemas.StockOut.model_validate(item).model_dump())
    return {
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "data": data,
    }


@router.get("/movements", response_model=schemas.PaginatedResponse)
def list_movements(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=5000),
    product_id: int | None = None,
    warehouse_id: int | None = None,
    db: Session = Depends(get_db),
):
    result = crud.get_stock_movements(db, page=page, per_page=per_page, product_id=product_id, warehouse_id=warehouse_id)
    data = [schemas.StockMovementOut.model_validate(item).model_dump() for item in result["data"]]
    return {
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "data": data,
    }


@router.post("/inventory")
def inventory(
    payload: list[schemas.InventoryItem],
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    items = [it.model_dump() for it in payload]
    result = inventory_adjust(db, items, user.id)
    return result


@router.post("/move")
def move(
    product_id: int,
    from_warehouse_id: int,
    to_warehouse_id: int,
    quantity: float,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    return move_stock(db, product_id, from_warehouse_id, to_warehouse_id, quantity, user.id)
