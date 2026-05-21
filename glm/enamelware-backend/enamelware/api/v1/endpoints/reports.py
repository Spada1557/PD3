import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from enamelware.database import get_db
from enamelware.models import Sale, SaleItem, Purchase, PurchaseItem, Product, Stock, Category
from enamelware.auth import get_current_user, require_role
from enamelware.models import User
from enamelware.enums import DocumentStatus
import openpyxl
from openpyxl.styles import Font, Alignment

router = APIRouter(prefix="/reports", tags=["Reports"])


def _make_xlsx(headers: list, rows: list, sheet_name: str = "Report") -> StreamingResponse:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal="center")
    for row in rows:
        ws.append(row)
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={sheet_name}_{datetime.now().strftime('%Y%m%d')}.xlsx"},
    )


@router.get("/sales")
def sales_report(
    date_from: str = None,
    date_to: str = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    query = db.query(Sale).filter(Sale.status == DocumentStatus.posted)
    if date_from:
        query = query.filter(Sale.date >= date_from)
    if date_to:
        query = query.filter(Sale.date <= date_to)
    sales = query.order_by(Sale.date.desc()).all()

    result = []
    for s in sales:
        items = db.query(SaleItem).filter(SaleItem.sale_id == s.id).all()
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            result.append({
                "sale_number": s.number,
                "date": s.date.isoformat() if s.date else None,
                "product": product.name if product else None,
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.amount,
                "cost": item.cost,
                "profit": item.profit,
                "margin": round((item.profit / item.amount * 100) if item.amount else 0, 2),
            })

    if format == "xlsx":
        headers = ["№ Продажи", "Дата", "Товар", "Кол-во", "Цена", "Сумма", "Себестоимость", "Прибыль", "Маржинальность %"]
        rows = [[r["sale_number"], r["date"], r["product"], r["quantity"], r["price"], r["amount"], r["cost"], r["profit"], r["margin"]] for r in result]
        return _make_xlsx(headers, rows, "Sales")

    total_amount = sum(r["amount"] for r in result)
    total_cost = sum(r["cost"] for r in result)
    total_profit = sum(r["profit"] for r in result)
    return {"data": result, "totals": {"amount": round(total_amount, 2), "cost": round(total_cost, 2), "profit": round(total_profit, 2)}}


@router.get("/stock")
def stock_report(
    date_to: str = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse", "manager")),
):
    stocks = db.query(Stock).all()
    result = []
    for s in stocks:
        product = db.query(Product).filter(Product.id == s.product_id).first()
        category = db.query(Category).filter(Category.id == product.category_id).first() if product and product.category_id else None
        result.append({
            "product": product.name if product else None,
            "article": product.article if product else None,
            "category": category.name if category else None,
            "quantity": s.quantity,
            "reserved": s.reserved,
            "available": s.quantity - s.reserved,
            "avg_cost": s.avg_cost,
            "total_value": round(s.quantity * s.avg_cost, 2),
        })

    if format == "xlsx":
        headers = ["Товар", "Артикул", "Категория", "Кол-во", "Резерв", "Доступно", "Ср. себестоимость", "Сумма"]
        rows = [[r["product"], r["article"], r["category"], r["quantity"], r["reserved"], r["available"], r["avg_cost"], r["total_value"]] for r in result]
        return _make_xlsx(headers, rows, "Stock")

    total_value = sum(r["total_value"] for r in result)
    return {"data": result, "total_value": round(total_value, 2)}


@router.get("/top-products")
def top_products_report(
    date_from: str = None,
    date_to: str = None,
    by: str = "revenue",
    limit: int = 10,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),
):
    query = db.query(Sale).filter(Sale.status == DocumentStatus.posted)
    if date_from:
        query = query.filter(Sale.date >= date_from)
    if date_to:
        query = query.filter(Sale.date <= date_to)
    sales = query.all()
    sale_ids = [s.id for s in sales]

    items = db.query(SaleItem).filter(SaleItem.sale_id.in_(sale_ids)).all() if sale_ids else []
    product_data = {}
    for item in items:
        if item.product_id not in product_data:
            product_data[item.product_id] = {"revenue": 0, "quantity": 0}
        product_data[item.product_id]["revenue"] += item.amount
        product_data[item.product_id]["quantity"] += item.quantity

    sort_key = "revenue" if by == "revenue" else "quantity"
    sorted_data = sorted(product_data.items(), key=lambda x: x[1][sort_key], reverse=True)[:limit]

    result = []
    for pid, vals in sorted_data:
        product = db.query(Product).filter(Product.id == pid).first()
        result.append({
            "product": product.name if product else None,
            "article": product.article if product else None,
            "revenue": round(vals["revenue"], 2),
            "quantity": vals["quantity"],
        })

    if format == "xlsx":
        headers = ["Товар", "Артикул", "Выручка", "Кол-во"]
        rows = [[r["product"], r["article"], r["revenue"], r["quantity"]] for r in result]
        return _make_xlsx(headers, rows, "TopProducts")

    return {"data": result}


@router.get("/purchases")
def purchases_report(
    date_from: str = None,
    date_to: str = None,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "warehouse")),
):
    query = db.query(Purchase).filter(Purchase.status == DocumentStatus.posted)
    if date_from:
        query = query.filter(Purchase.date >= date_from)
    if date_to:
        query = query.filter(Purchase.date <= date_to)
    purchases = query.order_by(Purchase.date.desc()).all()

    result = []
    for p in purchases:
        from enamelware.models import Supplier
        supplier = db.query(Supplier).filter(Supplier.id == p.supplier_id).first() if p.supplier_id else None
        result.append({
            "number": p.number,
            "date": p.date.isoformat() if p.date else None,
            "supplier": supplier.name if supplier else None,
            "total_amount": p.total_amount,
            "status": p.status.value,
        })

    if format == "xlsx":
        headers = ["№ Закупки", "Дата", "Поставщик", "Сумма", "Статус"]
        rows = [[r["number"], r["date"], r["supplier"], r["total_amount"], r["status"]] for r in result]
        return _make_xlsx(headers, rows, "Purchases")

    total = sum(r["total_amount"] for r in result)
    return {"data": result, "total_amount": round(total, 2)}