from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Stock, StockMovement, Product, Warehouse, Notification, User
from app.schemas import StockResponse, StockMovementResponse, InventoryRequest, StockTransferRequest, PaginatedResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/stock", tags=["stock"])


@router.get("", response_model=PaginatedResponse)
def list_stock(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    warehouse_id: int = None,
    search: str = None,
    low_stock: bool = False,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(Stock).options(joinedload(Stock.product), joinedload(Stock.warehouse))
    if warehouse_id:
        q = q.filter(Stock.warehouse_id == warehouse_id)
    if search:
        q = q.join(Product).filter(Product.name.ilike(f"%{search}%"))
    if low_stock:
        q = q.join(Product).filter(Stock.quantity <= Product.min_stock)
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    result = []
    for s in items:
        d = StockResponse.model_validate(s)
        d.available = round(s.quantity - s.reserved, 2)
        result.append(d)
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=result)


@router.get("/movements", response_model=PaginatedResponse)
def list_movements(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    product_id: int = None,
    warehouse_id: int = None,
    type: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(StockMovement).options(
        joinedload(StockMovement.product),
        joinedload(StockMovement.warehouse),
        joinedload(StockMovement.created_by_user),
    )
    if product_id:
        q = q.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        q = q.filter(StockMovement.warehouse_id == warehouse_id)
    if type:
        q = q.filter(StockMovement.type == type)
    q = q.order_by(StockMovement.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[StockMovementResponse.model_validate(m) for m in items])


@router.post("/inventory")
def inventory(body: InventoryRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    discrepancies = []
    for item in body.items:
        stock = db.query(Stock).filter(
            Stock.product_id == item.product_id,
            Stock.warehouse_id == body.warehouse_id,
        ).first()
        if not stock:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if not product:
                raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Товар id={item.product_id} не найден"})
            stock = Stock(product_id=item.product_id, warehouse_id=body.warehouse_id, quantity=0, reserved=0, avg_cost=product.cost)
            db.add(stock)
            db.flush()

        diff = round(item.fact_quantity - stock.quantity, 2)
        if diff != 0:
            direction = "+" if diff > 0 else "-"
            movement = StockMovement(
                product_id=item.product_id,
                warehouse_id=body.warehouse_id,
                type="in" if diff > 0 else "out",
                quantity=abs(diff),
                direction=direction,
                document_type="inventory",
                document_id=item.product_id,
                created_by=user["id"],
                comment="Инвентаризация: корректировка остатка",
            )
            db.add(movement)
            stock.quantity = item.fact_quantity
            discrepancies.append({
                "product_id": item.product_id,
                "book_quantity": round(stock.quantity - diff, 2),
                "fact_quantity": item.fact_quantity,
                "difference": diff,
            })

    db.commit()
    return {"message": "Инвентаризация проведена", "discrepancies": discrepancies}


@router.post("/transfer")
def transfer(body: StockTransferRequest, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from_stock = db.query(Stock).filter(
        Stock.product_id == body.product_id,
        Stock.warehouse_id == body.from_warehouse_id,
    ).first()
    if not from_stock:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Остаток на складе-отправителе не найден"})
    if from_stock.quantity < body.quantity:
        raise HTTPException(status_code=400, detail={"error": "insufficient_stock", "message": "Недостаточно товара на складе-отправителе"})

    to_stock = db.query(Stock).filter(
        Stock.product_id == body.product_id,
        Stock.warehouse_id == body.to_warehouse_id,
    ).first()
    if not to_stock:
        product = db.query(Product).filter(Product.id == body.product_id).first()
        to_stock = Stock(product_id=body.product_id, warehouse_id=body.to_warehouse_id, quantity=0, reserved=0, avg_cost=from_stock.avg_cost)
        db.add(to_stock)
        db.flush()

    from_stock.quantity -= body.quantity
    new_total_cost = to_stock.quantity * to_stock.avg_cost + body.quantity * from_stock.avg_cost
    to_stock.quantity += body.quantity
    to_stock.avg_cost = round(new_total_cost / to_stock.quantity, 2) if to_stock.quantity > 0 else 0

    db.add(StockMovement(
        product_id=body.product_id, warehouse_id=body.from_warehouse_id,
        type="move", quantity=body.quantity, direction="-",
        document_type="transfer", created_by=user["id"],
        comment=f"Перемещение на склад {body.to_warehouse_id}",
    ))
    db.add(StockMovement(
        product_id=body.product_id, warehouse_id=body.to_warehouse_id,
        type="move", quantity=body.quantity, direction="+",
        document_type="transfer", created_by=user["id"],
        comment=f"Перемещение со склада {body.from_warehouse_id}",
    ))

    db.commit()
    return {"message": "Перемещение выполнено"}


@router.get("/structure")
def stock_structure(warehouse_id: int = None, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    from app.models import Category
    q = db.query(Stock).options(joinedload(Stock.product).joinedload(Product.category))
    if warehouse_id:
        q = q.filter(Stock.warehouse_id == warehouse_id)

    categories = {}
    for s in q.all():
        cat_name = s.product.category.name if s.product and s.product.category else "Без категории"
        if cat_name not in categories:
            categories[cat_name] = 0
        categories[cat_name] += s.quantity

    total = sum(categories.values()) or 1
    result = [{"category": k, "quantity": v, "percent": round(v / total * 100, 1)} for k, v in categories.items()]
    return {"data": result, "total": round(total, 2)}
