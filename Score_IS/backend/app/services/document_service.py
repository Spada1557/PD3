from sqlalchemy.orm import Session
from app import models, crud


def generate_number(db: Session, prefix: str) -> str:
    last = db.query(models.Purchase if prefix == "ПУ" else models.Sale).order_by(
        (models.Purchase if prefix == "ПУ" else models.Sale).id.desc()
    ).first()
    next_id = (last.id + 1) if last else 1
    return f"{prefix}-{next_id:06d}"


def _default_warehouse_id(db: Session) -> int:
    return crud.get_default_warehouse(db).id


def post_purchase(db: Session, purchase: models.Purchase, user_id: int) -> models.Purchase:
    if purchase.status != models.DocumentStatus.draft:
        raise ValueError("Документ уже проведен или отменен")
    warehouse_id = _default_warehouse_id(db)
    for item in purchase.items:
        stock = crud.get_or_create_stock(db, item.product_id, warehouse_id)
        old_qty = stock.quantity
        new_qty = old_qty + item.quantity
        if new_qty > 0:
            stock.avg_cost = round(
                (stock.avg_cost * old_qty + item.price * item.quantity) / new_qty, 2
            )
        else:
            stock.avg_cost = item.price
        stock.quantity = new_qty
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=warehouse_id,
            type=models.StockMovementType.in_,
            quantity=item.quantity,
            direction=1,
            document_type="purchase",
            document_id=purchase.id,
            created_by=user_id,
        ))
    purchase.status = models.DocumentStatus.posted
    db.commit()
    db.refresh(purchase)
    return purchase


def cancel_purchase(db: Session, purchase: models.Purchase, user_id: int) -> models.Purchase:
    if purchase.status != models.DocumentStatus.posted:
        raise ValueError("Документ не проведен")
    warehouse_id = _default_warehouse_id(db)
    for item in purchase.items:
        stock = crud.get_stock_item(db, item.product_id, warehouse_id)
        if not stock:
            raise ValueError("Складская запись не найдена")
        if stock.quantity < item.quantity:
            raise ValueError("Недостаточно остатка для отмены прихода")
        new_qty = stock.quantity - item.quantity
        # Обратный пересчёт средневзвешенной себестоимости
        if new_qty > 0:
            new_avg = (stock.avg_cost * stock.quantity - item.price * item.quantity) / new_qty
            stock.avg_cost = round(max(new_avg, 0.0), 2)
        else:
            stock.avg_cost = 0.0
        stock.quantity = new_qty
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=warehouse_id,
            type=models.StockMovementType.out,
            quantity=item.quantity,
            direction=-1,
            document_type="purchase_cancel",
            document_id=purchase.id,
            created_by=user_id,
        ))
    purchase.status = models.DocumentStatus.cancelled
    db.commit()
    db.refresh(purchase)
    return purchase


def post_sale(db: Session, sale: models.Sale, user_id: int) -> models.Sale:
    if sale.status != models.DocumentStatus.draft:
        raise ValueError("Документ уже проведен или отменен")
    warehouse_id = _default_warehouse_id(db)
    total_cost = 0.0
    for item in sale.items:
        stock = crud.get_stock_item(db, item.product_id, warehouse_id)
        if not stock:
            raise ValueError(f"Товар {item.product_id} отсутствует на складе")
        available = stock.quantity - stock.reserved
        if item.quantity > available:
            raise ValueError(f"Недостаточно остатка для товара (доступно {available})")
        stock.quantity -= item.quantity
        cost = stock.avg_cost * item.quantity
        item.cost = round(cost, 2)
        total_cost += cost
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=warehouse_id,
            type=models.StockMovementType.out,
            quantity=item.quantity,
            direction=-1,
            document_type="sale",
            document_id=sale.id,
            created_by=user_id,
        ))
    sale.total_cost = round(total_cost, 2)
    sale.status = models.DocumentStatus.posted
    db.commit()
    db.refresh(sale)
    return sale


def cancel_sale(db: Session, sale: models.Sale, user_id: int) -> models.Sale:
    if sale.status != models.DocumentStatus.posted:
        raise ValueError("Документ не проведен")
    warehouse_id = _default_warehouse_id(db)
    for item in sale.items:
        stock = crud.get_or_create_stock(db, item.product_id, warehouse_id)
        stock.quantity += item.quantity
        db.add(models.StockMovement(
            product_id=item.product_id,
            warehouse_id=warehouse_id,
            type=models.StockMovementType.in_,
            quantity=item.quantity,
            direction=1,
            document_type="sale_cancel",
            document_id=sale.id,
            created_by=user_id,
        ))
    sale.status = models.DocumentStatus.cancelled
    db.commit()
    db.refresh(sale)
    return sale


def inventory_adjust(db: Session, items: list, user_id: int) -> dict:
    results = []
    for it in items:
        stock = crud.get_or_create_stock(db, it["product_id"], it["warehouse_id"])
        diff = round(it["fact_quantity"] - stock.quantity, 2)
        if diff != 0:
            direction = 1 if diff > 0 else -1
            db.add(models.StockMovement(
                product_id=it["product_id"],
                warehouse_id=it["warehouse_id"],
                type=models.StockMovementType.in_ if direction > 0 else models.StockMovementType.out,
                quantity=abs(diff),
                direction=direction,
                document_type="inventory",
                document_id=0,
                created_by=user_id,
            ))
            stock.quantity = it["fact_quantity"]
        results.append({"product_id": it["product_id"], "diff": diff})
    db.commit()
    return {"results": results}


def move_stock(
    db: Session,
    product_id: int,
    from_warehouse_id: int,
    to_warehouse_id: int,
    quantity: float,
    user_id: int,
) -> dict:
    from_stock = crud.get_stock_item(db, product_id, from_warehouse_id)
    if not from_stock or from_stock.quantity < quantity:
        raise ValueError("Недостаточно остатка на складе-отправителе")
    from_stock.quantity -= quantity
    to_stock = crud.get_or_create_stock(db, product_id, to_warehouse_id)
    to_stock.quantity += quantity
    db.add(models.StockMovement(
        product_id=product_id,
        warehouse_id=from_warehouse_id,
        type=models.StockMovementType.move,
        quantity=quantity,
        direction=-1,
        document_type="move",
        document_id=0,
        created_by=user_id,
    ))
    db.add(models.StockMovement(
        product_id=product_id,
        warehouse_id=to_warehouse_id,
        type=models.StockMovementType.move,
        quantity=quantity,
        direction=1,
        document_type="move",
        document_id=0,
        created_by=user_id,
    ))
    db.commit()
    return {"from_warehouse_id": from_warehouse_id, "to_warehouse_id": to_warehouse_id, "quantity": quantity}
