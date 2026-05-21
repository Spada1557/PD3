import random
import string
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func
from app.database import get_db
from app.models import Purchase, PurchaseItem, Product, Stock, StockMovement, Supplier, Notification, User
from app.models import StockMovementType, DocumentStatus
from app.schemas import PurchaseCreate, PurchaseUpdate, PurchaseResponse, PurchaseItemResponse, PaginatedResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/purchases", tags=["purchases"])


def _generate_purchase_number(db: Session) -> str:
    today = sa_func.date("now")
    count = db.query(Purchase).filter(sa_func.date(Purchase.created_at) == today).count() + 1
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ПУ-{suffix}{count:03d}"


@router.get("", response_model=PaginatedResponse)
def list_purchases(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str = None,
    supplier_id: int = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(Purchase).options(joinedload(Purchase.supplier), joinedload(Purchase.items).joinedload(PurchaseItem.product))
    if status:
        q = q.filter(Purchase.status == status)
    if supplier_id:
        q = q.filter(Purchase.supplier_id == supplier_id)
    if date_from:
        q = q.filter(Purchase.date >= date_from)
    if date_to:
        q = q.filter(Purchase.date <= date_to)
    q = q.order_by(Purchase.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[PurchaseResponse.model_validate(p) for p in items])


@router.get("/{purchase_id}", response_model=PurchaseResponse)
def get_purchase(purchase_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    p = db.query(Purchase).options(
        joinedload(Purchase.supplier),
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ закупки не найден"})
    return p


@router.post("", response_model=PurchaseResponse, status_code=201)
def create_purchase(body: PurchaseCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    if not body.items:
        raise HTTPException(status_code=400, detail={"error": "no_items", "message": "Документ должен содержать хотя бы одну позицию"})

    # Validate supplier
    supplier = db.query(Supplier).filter(Supplier.id == body.supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Поставщик не найден"})

    # Validate products
    for item in body.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Товар id={item.product_id} не найден"})

    number = _generate_purchase_number(db)
    total_amount = round(sum(i.amount for i in body.items), 2)

    purchase = Purchase(
        number=number,
        supplier_id=body.supplier_id,
        date=body.date,
        total_amount=total_amount,
        status=DocumentStatus.draft,
        comment=body.comment,
        created_by=user["id"],
    )
    db.add(purchase)
    db.flush()

    for item in body.items:
        db.add(PurchaseItem(
            purchase_id=purchase.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            amount=item.amount,
        ))

    db.commit()
    db.refresh(purchase)
    p = db.query(Purchase).options(
        joinedload(Purchase.supplier),
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase.id).first()
    return p


@router.put("/{purchase_id}", response_model=PurchaseResponse)
def update_purchase(purchase_id: int, body: PurchaseUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ закупки не найден"})
    if p.status.value != "draft":
        raise HTTPException(status_code=400, detail={"error": "not_draft", "message": "Можно редактировать только черновик"})

    if body.supplier_id is not None:
        p.supplier_id = body.supplier_id
    if body.date is not None:
        p.date = body.date
    if body.comment is not None:
        p.comment = body.comment

    if body.items is not None:
        db.query(PurchaseItem).filter(PurchaseItem.purchase_id == purchase_id).delete()
        for item in body.items:
            db.add(PurchaseItem(
                purchase_id=purchase_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                amount=item.amount,
            ))
        p.total_amount = round(sum(i.amount for i in body.items), 2)

    db.commit()
    db.refresh(p)
    p = db.query(Purchase).options(
        joinedload(Purchase.supplier),
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    return p


@router.post("/{purchase_id}/post", response_model=PurchaseResponse)
def post_purchase(purchase_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).options(
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if p.status.value != "draft":
        raise HTTPException(status_code=400, detail={"error": "already_posted", "message": "Документ уже проведён или отменён"})

    warehouse_id = 1  # Default warehouse

    try:
        for item in p.items:
            stock = db.query(Stock).filter(
                Stock.product_id == item.product_id,
                Stock.warehouse_id == warehouse_id,
            ).first()

            if not stock:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                stock = Stock(
                    product_id=item.product_id,
                    warehouse_id=warehouse_id,
                    quantity=0.0,
                    reserved=0.0,
                    avg_cost=0.0,
                )
                db.add(stock)
                db.flush()

            new_total_cost = stock.quantity * stock.avg_cost + item.quantity * item.price
            stock.quantity += item.quantity
            stock.avg_cost = round(new_total_cost / stock.quantity, 2) if stock.quantity > 0 else 0

            db.add(StockMovement(
                product_id=item.product_id,
                warehouse_id=warehouse_id,
                type=StockMovementType.in_,
                quantity=item.quantity,
                direction="+",
                document_type="purchase",
                document_id=purchase_id,
                created_by=user["id"],
                comment=f"Поступление по документу {p.number}",
            ))

        p.status = DocumentStatus.posted
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "post_error", "message": "Ошибка проведения документа"})

    p = db.query(Purchase).options(
        joinedload(Purchase.supplier),
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    return p


@router.post("/{purchase_id}/cancel", response_model=PurchaseResponse)
def cancel_purchase(purchase_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "warehouse"))):
    p = db.query(Purchase).options(
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if p.status.value != "posted":
        raise HTTPException(status_code=400, detail={"error": "not_posted", "message": "Можно отменить только проведённый документ"})

    warehouse_id = 1

    try:
        for item in p.items:
            stock = db.query(Stock).filter(
                Stock.product_id == item.product_id,
                Stock.warehouse_id == warehouse_id,
            ).first()

            if not stock or stock.quantity < item.quantity:
                db.rollback()
                raise HTTPException(status_code=400, detail={
                    "error": "insufficient_stock",
                    "message": f"Недостаточно остатка товара {item.product.name} для отмены поступления"
                })

            stock.quantity -= item.quantity
            stock.avg_cost = round(
                (stock.quantity * stock.avg_cost) / stock.quantity, 2
            ) if stock.quantity > 0 else 0

            db.add(StockMovement(
                product_id=item.product_id,
                warehouse_id=warehouse_id,
                type=StockMovementType.out,
                quantity=item.quantity,
                direction="-",
                document_type="purchase_cancel",
                document_id=purchase_id,
                created_by=user["id"],
                comment=f"Отмена поступления {p.number}",
            ))

        p.status = DocumentStatus.cancelled
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "cancel_error", "message": "Ошибка отмены документа"})

    p = db.query(Purchase).options(
        joinedload(Purchase.supplier),
        joinedload(Purchase.items).joinedload(PurchaseItem.product),
    ).filter(Purchase.id == purchase_id).first()
    return p


@router.delete("/{purchase_id}")
def delete_purchase(purchase_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    p = db.query(Purchase).filter(Purchase.id == purchase_id).first()
    if not p:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if p.status.value == "posted":
        raise HTTPException(status_code=400, detail={"error": "posted", "message": "Нельзя удалить проведённый документ"})
    db.delete(p)
    db.commit()
    return {"message": "Документ удалён"}
