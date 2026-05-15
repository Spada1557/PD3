from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from enamelware.database import get_db
from enamelware.models import Purchase, PurchaseItem, Supplier, Product, Stock, StockMovement, Notification
from enamelware.schemas import PurchaseCreate, PurchaseUpdate, PurchaseOut, PurchaseItemOut
from enamelware.auth import get_current_user, require_role
from enamelware.models import User
from enamelware.enums import MovementType, DocumentType, DocumentStatus

router = APIRouter(prefix="/purchases", tags=["Purchases"])


def _generate_purchase_number(db: Session) -> str:
    last = db.query(Purchase).order_by(Purchase.id.desc()).first()
    num = (last.id + 1) if last else 1
    return f"ПУ-{num:04d}"


def _purchase_to_out(p: Purchase, db: Session) -> dict:
    supplier = db.query(Supplier).filter(Supplier.id == p.supplier_id).first() if p.supplier_id else None
    items = []
    for item in p.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items.append(PurchaseItemOut(
            id=item.id, purchase_id=item.purchase_id, product_id=item.product_id,
            quantity=item.quantity, price=item.price, amount=item.amount,
            product_name=product.name if product else None,
        ))
    return PurchaseOut(
        id=p.id, number=p.number, supplier_id=p.supplier_id,
        date=p.date, total_amount=p.total_amount, status=p.status.value,
        comment=p.comment, created_by=p.created_by,
        created_at=p.created_at, updated_at=p.updated_at,
        items=items, supplier_name=supplier.name if supplier else None,
    )


def _check_low_stock(product_id: int, db: Session, user_id: int = None):
    stocks = db.query(Stock).filter(Stock.product_id == product_id).all()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return
    total_qty = sum(s.quantity for s in stocks)
    if total_qty < product.min_stock:
        users = db.query(User).filter(User.role.in_(["admin", "warehouse"])).all()
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
def list_purchases(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    supplier_id: int = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    query = db.query(Purchase)
    if status_filter:
        query = query.filter(Purchase.status == status_filter)
    if supplier_id:
        query = query.filter(Purchase.supplier_id == supplier_id)
    if date_from:
        query = query.filter(Purchase.date >= date_from)
    if date_to:
        query = query.filter(Purchase.date <= date_to)
    total = query.count()
    purchases = query.order_by(Purchase.date.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {"total": total, "page": page, "per_page": per_page, "data": [_purchase_to_out(p, db) for p in purchases]}


@router.get("/{purchase_id}", response_model=PurchaseOut)
def get_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Purchase not found"})
    return _purchase_to_out(p, db)


@router.post("", response_model=PurchaseOut, status_code=status.HTTP_201_CREATED)
def create_purchase(data: PurchaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    try:
        total_amount = 0
        items = []
        for item_data in data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": f"Product {item_data.product_id} not found"})
            amount = round(item_data.quantity * item_data.price, 2)
            total_amount += amount
            items.append(PurchaseItem(
                product_id=item_data.product_id, quantity=item_data.quantity,
                price=item_data.price, amount=amount,
            ))

        p = Purchase(
            number=_generate_purchase_number(db),
            supplier_id=data.supplier_id,
            date=data.date or datetime.utcnow(),
            total_amount=round(total_amount, 2),
            status=DocumentStatus.draft,
            comment=data.comment,
            created_by=current_user.id,
            items=items,
        )
        db.add(p)
        db.commit()
        db.refresh(p)
        return _purchase_to_out(p, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})


@router.put("/{purchase_id}", response_model=PurchaseOut)
def update_purchase(purchase_id: int, data: PurchaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Purchase not found"})
    if p.status.value != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only edit draft purchases"})

    if data.supplier_id is not None:
        p.supplier_id = data.supplier_id
    if data.date is not None:
        p.date = data.date
    if data.comment is not None:
        p.comment = data.comment

    if data.items is not None:
        db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).delete()
        total_amount = 0
        for item_data in data.items:
            product = db.query(Product).filter(Product.id == item_data.product_id).first()
            if not product:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": f"Product {item_data.product_id} not found"})
            amount = round(item_data.quantity * item_data.price, 2)
            total_amount += amount
            new_item = PurchaseItem(
                purchase_id=purchase_id, product_id=item_data.product_id,
                quantity=item_data.quantity, price=item_data.price, amount=amount,
            )
            db.add(new_item)
        p.total_amount = round(total_amount, 2)

    db.commit()
    db.refresh(p)
    return _purchase_to_out(p, db)


@router.post("/{purchase_id}/post")
def post_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Purchase not found"})
    if p.status.value != "draft":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only post draft purchases"})
    try:
        for item in p.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id, Stock.warehouse_id == 1).first()
            if not stock:
                stock = Stock(product_id=item.product_id, warehouse_id=1, quantity=0, reserved=0, avg_cost=item.price)
                db.add(stock)
                db.flush()

            new_avg = (stock.avg_cost * stock.quantity + item.price * item.quantity) / (stock.quantity + item.quantity) if (stock.quantity + item.quantity) > 0 else item.price
            stock.avg_cost = round(new_avg, 2)
            stock.quantity += item.quantity

            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                type=MovementType.incoming, quantity=item.quantity, direction=1,
                document_type=DocumentType.purchase, document_id=p.id,
                created_by=current_user.id,
            )
            db.add(movement)
            _check_low_stock(item.product_id, db, current_user.id)

        p.status = DocumentStatus.posted
        db.commit()
        return _purchase_to_out(p, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})


@router.post("/{purchase_id}/cancel")
def cancel_purchase(purchase_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "not_found", "message": "Purchase not found"})
    if p.status.value != "posted":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "bad_request", "message": "Can only cancel posted purchases"})
    try:
        for item in p.items:
            stock = db.query(Stock).filter(Stock.product_id == item.product_id, Stock.warehouse_id == 1).first()
            if not stock:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "insufficient_stock", "message": f"No stock record for product {item.product_id}"})
            if stock.quantity < item.quantity:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"error": "insufficient_stock", "message": f"Insufficient stock for product {item.product_id}"})
            stock.quantity -= item.quantity

            movement = StockMovement(
                product_id=item.product_id, warehouse_id=1,
                type=MovementType.outgoing, quantity=item.quantity, direction=-1,
                document_type=DocumentType.purchase, document_id=p.id,
                comment=f"Отмена прихода {p.number}",
                created_by=current_user.id,
            )
            db.add(movement)

        p.status = DocumentStatus.cancelled
        db.commit()
        return _purchase_to_out(p, db)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"error": "server_error", "message": str(e)})