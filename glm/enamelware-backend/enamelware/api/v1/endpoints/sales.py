from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Sale, SaleItem, Client, Product, Stock, StockMovement, Notification
from enamelware.schemas import SaleCreate, SaleUpdate, SaleOut, SaleItemOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User
from enamelware.enums import MovementType, DocumentType, DocumentStatus

router = APIRouter(prefix="/sales", tags=["Sales"])


def _generate_sale_number(db: Session) -> str:
    last = db.query(Sale).order_by(Sale.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"ПР-{num:04d}"


def _sale_to_out(s: Sale, db: Session) -> dict:
    client = db.query(Client).filter(Client.id == s.client_id).first() if s.client_id else None
    items = []
    for item in s.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append(SaleItemOut(
            id=item.id, sale_id=item.sale_id, product_id=item.product_id,
            quantity=item.quantity, price=item.price, amount=item.amount,
            cost=item.cost, profit=item.profit,
            product_name=product.name if product else None,
        ))
    return SaleOut(
        id=s.id, number=s.number, client_id=s.client_id,
        date=s.date, total_amount=s.total_amount, cost_amount=s.cost_amount,
        profit_amount=s.profit_amount, status=s.status.value,
        comment=s.comment, created_by=s.created_by,
        created_at=s.created_at, updated_at=s.updated_at,
        items=items, client_name=client.name if client else None,
    )


def _check_low_stock(product_id: int, db: Session):
    stocks = db.query(Stock).filter(Stock.product_id == product_id).all()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return
    total_qty = sum(s.quantity for s in stocks)
    if total_qty < product.min_stock:
        users = db.query(User).filter(User.role.in_(["admin", "manager"])).all()
        for u in users:
            existing = db.query(Notification).filter(
                Notification.type == "low_stock",
                Notification.title.like(f"%{product.name}%"),
                Notification.is_read == False,
            ).first()
            if not existing:
                notif = Notification(
                    user_id=u.id, type="low_stock",
                    title=f"Низкий остаток: {product.name}",
                    message=f"Остаток товара '{product.name}' ({total_qty}) ниже минимального ({product.min_stock})",
                )
                db.add(notif)


@router.get("", response_model=dict)
def list_sales(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    client_id: int = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    query = db.query(Sale)
    if status_filter:
        query = query.filter(Sale.status == status_filter)
    if client_id:
        query = query.filter(Sale.client_id == client_id)
    if date_from:
        query = query.filter(Sale.date >= date_from)
    if date_to:
        query = query.filter(Sale.date <= date_to)
    total = query.count()
    sales = query.order_by(Sale.date.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [_sale_to_out(s, db) for s in sales]}


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Sale not found"})
    return _sale_to_out(s, db)


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(data: SaleCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    try:
        total_amount = 0
        cost_amount = 0
        items = []
        for item_data in data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": f"Product {item_data.product_id} not found"})
            stock = db.query(Stock).filter(Stock.product_id == item_data.product_id, Stock.warehouse_id == 1).first()
            avg_cost = stock.avg_cost if stock else product.cost
            amount = round(item_data.quantity * item_data.price, 2)
            cost = round(item_data.quantity * avg_cost, 2)
            profit = round(amount - cost, 2)
            total_amount += amount
            cost_amount += cost
            items.append(SaleItem(
                product_id=item_data.product_id, quantity=item_data.quantity,
                price=item_data.price, amount=amount, cost=cost, profit=profit,
            ))

        s = Sale(
            number=_generate_sale_number(db),
            client_id=data.client_id,
            date=data.date or datetime.utcnow(),
            total_amount=round(total_amount, 2),
            cost_amount=round(cost_amount, 2),
            profit_amount=round(total_amount - cost_amount, 2),
            status=DocumentStatus.draft,
            comment=data.comment,
            created_by=current_user.id,
            items=items,
        )
        db.add(s)
        db.commit()
        db.refresh(s)
        return _sale_to_out(s, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})


@router.put("/{sale_id}", response_model=SaleOut)
def update_sale(sale_id: int, data: SaleUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Sale not found"})
    if s.status.value != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only edit draft sales"})

    if data.client_id is not None:
        s.client_id = data.client_id
    if data.date is not None:
        s.date = data.date
    if data.comment is not None:
        s.comment = data.comment

    if data.items is not None:
        db.query(SaleItem).filter(SaleItem.sale_id == sale_id).delete()
        total_amount = 0
        cost_amount = 0
        for item_data in data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": f"Product {item_data.product_id} not found"})
            stock = db.query(Stock).filter(Stock.product_id == item_data.product_id, Stock.warehouse_id == 1).first()
            avg_cost = stock.avg_cost if stock else product.cost
            amount = round(item_data.quantity * item_data.price, 2)
            cost = round(item_data.quantity * avg_cost, 2)
            profit = round(amount - cost, 2)
            total_amount += amount
            cost_amount += cost
            new_item = SaleItem(
                sale_id=sale_id, product_id=item_data.product_id,
                quantity=item_data.quantity, price=item_data.price,
                amount=amount, cost=cost, profit=profit,
            )
            db.add(new_item)
        s.total_amount = round(total_amount, 2)
        s.cost_amount = round(cost_amount, 2)
        s.profit_amount = round(total_amount - cost_amount, 2)

    db.commit()
    db.refresh(s)
    return _sale_to_out(s, db)


@router.post("/{sale_id}/post")
def post_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Sale not found"})
    if s.status.value != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only post draft sales"})
    try:
        for item in s.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id, Stock.warehouse_id == 1).first()
            if not stock:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "no_stock", "message": f"No stock for product {item.product_id}"})
            available = stock.quantity - stock.reserved
            if available < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "insufficient_stock", "message": f"Insufficient stock for product {item.product_id}. Available: {available}, requested: {item.quantity}"})
            stock.quantity -= item.quantity

            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                type=MovementType.outgoing, quantity=item.quantity, direction=-1,
                document_type=DocumentType.sale, document_id=s.id,
                created_by=current_user.id,
            )
            db.add(movement)
            _check_low_stock(item.product_id, db)

        s.status = DocumentStatus.posted
        db.commit()

        notif_users = db.query(User).filter(User.role.in_(["admin", "manager"])).all()
        for u in notif_users:
            n = Notification(
                user_id=u.id, type="new_sale",
                title=f"Новая продажа {s.number}",
                message=f"Проведена продажа {s.number} на сумму {s.total_amount:.2f}",
            )
            db.add(n)
        db.commit()
        return _sale_to_out(s, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})


@router.post("/{sale_id}/cancel")
def cancel_sale(sale_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Sale not found"})
    if s.status.value != "posted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only cancel posted sales"})
    try:
        for item in s.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id, Stock.warehouse_id == 1).first()
            if not stock:
                stock = Stock(product_id=item.product_id, warehouse_id=1, quantity=0, reserved=0, avg_cost=item.cost / item.quantity if item.quantity > 0 else 0)
                db.add(stock)
                db.flush()
            stock.quantity += item.quantity

            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                type=MovementType.incoming, quantity=item.quantity, direction=1,
                document_type=DocumentType.sale, document_id=s.id,
                comment=f"Отмена продажи {s.number}",
                created_by=current_user.id,
            )
            db.add(movement)

        s.status = DocumentStatus.cancelled
        db.commit()
        return _sale_to_out(s, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})