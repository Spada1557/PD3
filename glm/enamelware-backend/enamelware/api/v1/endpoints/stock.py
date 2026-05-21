from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from enamelware.database import get_db
from enamelware.models import Stock, StockMovement, Product, Warehouse, Notification
from enamelware.schemas import StockOut, StockMovementOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User
from enamelware.enums import MovementType, DocumentType

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.get("", response_model=dict)
def list_stock(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    warehouse_id: int = None,
    product_id: int = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Stock)
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    if search:
        query = query.join(Product).filter(Product.name.ilike(f"%{search}%"))
    total = query.count()
    stocks = query.all()
    result = []
    for s in stocks:
        available = s.quantity - s.reserved
        p = db.query(Product).filter(Product.id == s.product_id).first()
        w = db.query(Warehouse).filter(Warehouse.id == s.warehouse_id).first()
        result.append(StockOut(
            id=s.id, product_id=s.product_id, warehouse_id=s.warehouse_id,
            quantity=s.quantity, reserved=s.reserved, avg_cost=s.avg_cost,
            available=available, product_name=p.name if p else None,
            warehouse_name=w.name if w else None,
        ))
    start = (page - 1) * per_page
    return {"total": total, "page": page, "per_page": per_page, "data": result[start:start + per_page]}


@router.get("/movements", response_model=dict)
def list_movements(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    product_id: int = None,
    warehouse_id: int = None,
    type: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    query = db.query(StockMovement)
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockMovement.warehouse_id == warehouse_id)
    if type:
        query = query.filter(StockMovement.type == type)
    total = query.count()
    movements = query.order_by(StockMovement.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    result = []
    for m in movements:
        p = db.query(Product).filter(Product.id == m.product_id).first()
        result.append(StockMovementOut(
            id=m.id, product_id=m.product_id, warehouse_id=m.warehouse_id,
            type=m.type.value, quantity=m.quantity, direction=m.direction,
            document_type=m.document_type.value if m.document_type else None,
            document_id=m.document_id, comment=m.comment,
            created_by=m.created_by, created_at=m.created_at,
            product_name=p.name if p else None,
        ))
    return {"total": total, "page": page, "per_page": per_page, "data": result}


@router.get("/last-movements", response_model=list[StockMovementOut])
def last_movements(limit: int = Query(5, ge=1, le=20), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movements = db.query(StockMovement).order_by(StockMovement.created_at.desc()).limit(limit).all()
    result = []
    for m in movements:
        p = db.query(Product).filter(Product.id == m.product_id).first()
        result.append(StockMovementOut(
            id=m.id, product_id=m.product_id, warehouse_id=m.warehouse_id,
            type=m.type.value, quantity=m.quantity, direction=m.direction,
            document_type=m.document_type.value if m.document_type else None,
            document_id=m.document_id, comment=m.comment,
            created_by=m.created_by, created_at=m.created_at,
            product_name=p.name if p else None,
        ))
    return result


@router.get("/structure", response_model=dict)
def stock_structure(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stocks = db.query(Stock).all()
    categories = {}
    for s in stocks:
        p = db.query(Product).filter(Product.id == s.product_id).first()
        if p and p.category_id:
            cat = db.query(Product).filter(Product.id == s.product_id).first()
            from enamelware.models import Category
            c = db.query(Category).filter(Category.id == p.category_id).first()
            name = c.name if c else "Без категории"
        else:
            name = "Без категории"
        categories[name] = categories.get(name, 0) + s.quantity * s.avg_cost
    return {"labels": list(categories.keys()), "values": list(categories.values())}


@router.post("/inventory", response_model=dict)
def inventory_check(
    adjustments: list[dict],
    warehouse_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    try:
        for adj in adjustments:
            product_id = adj.get("product_id")
            actual_quantity = adj.get("actual_quantity")
            if product_id is None or actual_quantity is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "product_id and actual_quantity required"})
            stock = db.query(Stock).filter(Stock.product_id == product_id, Stock.warehouse_id == warehouse_id).first()
            if not stock:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": f"Stock not found for product {product_id}"})
            diff = actual_quantity - stock.quantity
            if diff != 0:
                movement = StockMovement(
                    product_id=product_id, warehouse_id=warehouse_id,
                    type=MovementType.incoming if diff > 0 else MovementType.outgoing,
                    quantity=abs(diff), direction=1 if diff > 0 else -1,
                    document_type=DocumentType.inventory, comment=f"Инвентаризация: {diff:+.2f}",
                    created_by=current_user.id,
                )
                db.add(movement)
                stock.quantity = actual_quantity
        db.commit()
        return {"message": "Inventory adjustments applied"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})


@router.post("/transfer", response_model=dict)
def transfer_stock(
    transfer_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    try:
        product_id = transfer_data.get("product_id")
        from_warehouse_id = transfer_data.get("from_warehouse_id")
        to_warehouse_id = transfer_data.get("to_warehouse_id")
        quantity = transfer_data.get("quantity")
        if not all([product_id, from_warehouse_id, to_warehouse_id, quantity]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "All fields required"})
        if from_warehouse_id == to_warehouse_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Source and destination warehouses must be different"})
        if quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Quantity must be positive"})
        from_stock = db.query(Stock).filter(Stock.product_id == product_id, Stock.warehouse_id == from_warehouse_id).first()
        if not from_stock:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Source stock not found"})
        available = from_stock.quantity - from_stock.reserved
        if available < quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "insufficient_stock", "message": f"Available quantity is {available}"})
        to_stock = db.query(Stock).filter(Stock.product_id == product_id, Stock.warehouse_id == to_warehouse_id).first()
        if not to_stock:
            product = db.query(Product).filter(Product.id == product_id).first()
            to_stock = Stock(product_id=product_id, warehouse_id=to_warehouse_id, quantity=0, reserved=0, avg_cost=product.cost if product else 0)
            db.add(to_stock)
            db.flush()

        new_avg = (to_stock.avg_cost * to_stock.quantity + from_stock.avg_cost * quantity) / (to_stock.quantity + quantity) if (to_stock.quantity + quantity) > 0 else from_stock.avg_cost
        to_stock.avg_cost = round(new_avg, 2)
        to_stock.quantity += quantity
        from_stock.quantity -= quantity

        outgoing = StockMovement(
            product_id=product_id, warehouse_id=from_warehouse_id,
            type=MovementType.move, quantity=quantity, direction=-1,
            document_type=DocumentType.transfer, created_by=current_user.id,
        )
        db.add(outgoing)

        incoming = StockMovement(
            product_id=product_id, warehouse_id=to_warehouse_id,
            type=MovementType.move, quantity=quantity, direction=1,
            document_type=DocumentType.transfer, created_by=current_user.id,
        )
        db.add(incoming)

        db.commit()
        return {"message": "Transfer completed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})