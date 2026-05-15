import random
import string
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func
from app.database import get_db
from app.models import Sale, SaleItem, Product, Stock, StockMovement, Client, Notification
from app.models import StockMovementType, DocumentStatus
from app.schemas import SaleCreate, SaleUpdate, SaleResponse, SaleItemResponse, PaginatedResponse
from app.api.deps import get_current_user, require_role

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


def _generate_sale_number(db: Session) -> str:
    today = sa_func.date("now")
    count = db.query(Sale).filter(sa_func.date(Sale.created_at) == today).count() + 1
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ПР-{suffix}{count:03d}"


@router.get("", response_model=PaginatedResponse)
def list_sales(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: str = None,
    client_id: int = None,
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    q = db.query(Sale).options(joinedload(Sale.client), joinedload(Sale.items).joinedload(SaleItem.product))
    if status:
        q = q.filter(Sale.status == status)
    if client_id:
        q = q.filter(Sale.client_id == client_id)
    if date_from:
        q = q.filter(Sale.date >= date_from)
    if date_to:
        q = q.filter(Sale.date <= date_to)
    q = q.order_by(Sale.created_at.desc())
    total = q.count()
    items = q.offset((page - 1) * per_page).limit(per_page).all()
    return PaginatedResponse(total=total, page=page, per_page=per_page, data=[SaleResponse.model_validate(s) for s in items])


@router.get("/{sale_id}", response_model=SaleResponse)
def get_sale(sale_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    s = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ продажи не найден"})
    return s


@router.post("", response_model=SaleResponse, status_code=201)
def create_sale(body: SaleCreate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "manager"))):
    if not body.items:
        raise HTTPException(status_code=400, detail={"error": "no_items", "message": "Документ должен содержать хотя бы одну позицию"})

    client = db.query(Client).filter(Client.id == body.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Клиент не найден"})

    for item in body.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail={"error": "not_found", "message": f"Товар id={item.product_id} не найден"})

    number = _generate_sale_number(db)
    total_amount = round(sum(i.amount for i in body.items), 2)

    sale = Sale(
        number=number,
        client_id=body.client_id,
        date=body.date,
        total_amount=total_amount,
        total_cost=0.0,
        total_profit=0.0,
        status=DocumentStatus.draft,
        comment=body.comment,
        created_by=user["id"],
    )
    db.add(sale)
    db.flush()

    for item in body.items:
        db.add(SaleItem(
            sale_id=sale.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
            amount=item.amount,
            cost=0.0,
        ))

    db.commit()
    db.refresh(sale)
    s = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale.id).first()
    return s


@router.put("/{sale_id}", response_model=SaleResponse)
def update_sale(sale_id: int, body: SaleUpdate, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ продажи не найден"})
    if s.status.value != "draft":
        raise HTTPException(status_code=400, detail={"error": "not_draft", "message": "Можно редактировать только черновик"})

    if body.client_id is not None:
        s.client_id = body.client_id
    if body.date is not None:
        s.date = body.date
    if body.comment is not None:
        s.comment = body.comment

    if body.items is not None:
        db.query(SaleItem).filter(SaleItem.sale_id == sale_id).delete()
        for item in body.items:
            db.add(SaleItem(
                sale_id=sale_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                amount=item.amount,
                cost=0.0,
            ))
        s.total_amount = round(sum(i.amount for i in body.items), 2)

    db.commit()
    db.refresh(s)
    s = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    return s


@router.post("/{sale_id}/post", response_model=SaleResponse)
def post_sale(sale_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).options(
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if s.status.value != "draft":
        raise HTTPException(status_code=400, detail={"error": "already_posted", "message": "Документ уже проведён или отменён"})

    warehouse_id = 1
    total_cost = 0.0

    try:
        # Check stock availability FIRST
        for item in s.items:
            stock = db.query(Stock).filter(
                Stock.product_id == item.product_id,
                Stock.warehouse_id == warehouse_id,
            ).first()

            available = (stock.quantity - stock.reserved) if stock else 0.0
            if available < item.quantity:
                product_name = f"ID={item.product_id}"
                if item.product:
                    product_name = f"{item.product.name} ({item.product.article})"
                db.rollback()
                raise HTTPException(status_code=400, detail={
                    "error": "insufficient_stock",
                    "message": f"Товар '{product_name}': доступно {available}, запрошено {item.quantity}"
                })

        # Process sale
        for item in s.items:
            stock = db.query(Stock).filter(
                Stock.product_id == item.product_id,
                Stock.warehouse_id == warehouse_id,
            ).first()

            item_cost = round(item.quantity * stock.avg_cost, 2)
            total_cost += item_cost
            item.cost = item_cost

            stock.quantity -= item.quantity

            db.add(StockMovement(
                product_id=item.product_id,
                warehouse_id=warehouse_id,
                type=StockMovementType.out,
                quantity=item.quantity,
                direction="-",
                document_type="sale",
                document_id=sale_id,
                created_by=user["id"],
                comment=f"Продажа по документу {s.number}",
            ))

        s.total_cost = round(total_cost, 2)
        s.total_profit = round(s.total_amount - total_cost, 2)
        s.status = DocumentStatus.posted

        # Check low stock and create notifications
        for item in s.items:
            stock = db.query(Stock).join(Product).filter(
                Stock.product_id == item.product_id,
                Stock.warehouse_id == warehouse_id,
            ).first()
            if stock:
                product = item.product
                if product and stock.quantity <= product.min_stock:
                    db.add(Notification(
                        type="low_stock",
                        title=f"Низкий остаток: {product.name}",
                        message=f"Товар '{product.name}' ({product.article}): остаток {stock.quantity} шт. (мин. запас: {product.min_stock})",
                        reference_type="product",
                        reference_id=product.id,
                    ))

        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "post_error", "message": "Ошибка проведения документа"})

    s = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    return s


@router.post("/{sale_id}/cancel", response_model=SaleResponse)
def cancel_sale(sale_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin", "manager"))):
    s = db.query(Sale).options(
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if s.status.value != "posted":
        raise HTTPException(status_code=400, detail={"error": "not_posted", "message": "Можно отменить только проведённый документ"})

    warehouse_id = 1

    try:
        for item in s.items:
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
                document_type="sale_cancel",
                document_id=sale_id,
                created_by=user["id"],
                comment=f"Отмена продажи {s.number}",
            ))

        s.status = DocumentStatus.cancelled
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail={"error": "cancel_error", "message": "Ошибка отмены документа"})

    s = db.query(Sale).options(
        joinedload(Sale.client),
        joinedload(Sale.items).joinedload(SaleItem.product),
    ).filter(Sale.id == sale_id).first()
    return s


@router.delete("/{sale_id}")
def delete_sale(sale_id: int, db: Session = Depends(get_db), user: dict = Depends(require_role("admin"))):
    s = db.query(Sale).filter(Sale.id == sale_id).first()
    if not s:
        raise HTTPException(status_code=404, detail={"error": "not_found", "message": "Документ не найден"})
    if s.status.value == "posted":
        raise HTTPException(status_code=400, detail={"error": "posted", "message": "Нельзя удалить проведённый документ"})
    db.delete(s)
    db.commit()
    return {"message": "Документ удалён"}
