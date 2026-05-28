from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app import models, schemas
from openpyxl import Workbook
from io import BytesIO
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


def _to_excel(rows: list[dict], filename: str):
    wb = Workbook()
    ws = wb.active
    if rows:
        headers = list(rows[0].keys())
        ws.append(headers)
        for r in rows:
            ws.append([r.get(h) for h in headers])
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def build_sales_report(db: Session, date_from: str | None = None, date_to: str | None = None):
    q = db.query(models.Sale).filter(models.Sale.status == models.DocumentStatus.posted)
    if date_from:
        q = q.filter(models.Sale.date >= date_from)
    if date_to:
        q = q.filter(models.Sale.date <= date_to)
    sales = q.order_by(models.Sale.date.desc()).all()
    rows = []
    for s in sales:
        for item in s.items:
            margin = item.amount - item.cost
            margin_percent = round((margin / item.amount) * 100, 2) if item.amount else 0
            rows.append({
                "number": s.number,
                "date": s.date.strftime("%Y-%m-%d %H:%M:%S") if s.date else "",
                "client": s.client.name if s.client else "",
                "product": item.product.name if item.product else "",
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.amount,
                "cost": item.cost,
                "margin": margin,
                "margin_percent": margin_percent,
            })
    return rows


@router.get("/sales")
def sales_report(
    date_from: str | None = None,
    date_to: str | None = None,
    format: str = Query("json", pattern=r"^(json|xlsx)$"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    rows = build_sales_report(db, date_from, date_to)
    if format == "json":
        return {"data": rows}
    return _to_excel(rows, "sales_report.xlsx")


@router.get("/stock")
def stock_report(
    warehouse_id: int | None = None,
    format: str = Query("json", pattern=r"^(json|xlsx)$"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse", "manager"])),
):
    q = db.query(models.Stock).order_by(models.Stock.id)
    if warehouse_id:
        q = q.filter(models.Stock.warehouse_id == warehouse_id)
    rows = []
    for s in q.all():
        rows.append({
            "product": s.product.name if s.product else "",
            "article": s.product.article if s.product else "",
            "warehouse": s.warehouse.name if s.warehouse else "",
            "quantity": s.quantity,
            "available": s.quantity - s.reserved,
            "avg_cost": s.avg_cost,
            "value": round(s.quantity * s.avg_cost, 2),
        })
    if format == "json":
        return {"data": rows}
    return _to_excel(rows, "stock_report.xlsx")


@router.get("/top-products")
def top_products(
    date_from: str | None = None,
    date_to: str | None = None,
    by: str = Query("revenue", pattern=r"^(revenue|quantity)$"),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    q = db.query(
        models.SaleItem.product_id,
        func.sum(models.SaleItem.quantity).label("qty"),
        func.sum(models.SaleItem.amount).label("rev"),
    ).join(models.Sale).filter(models.Sale.status == models.DocumentStatus.posted)
    if date_from:
        q = q.filter(models.Sale.date >= date_from)
    if date_to:
        q = q.filter(models.Sale.date <= date_to)
    q = q.group_by(models.SaleItem.product_id)
    if by == "revenue":
        q = q.order_by(desc("rev"))
    else:
        q = q.order_by(desc("qty"))
    results = q.limit(limit).all()
    out = []
    for r in results:
        p = db.query(models.Product).filter(models.Product.id == r.product_id).first()
        out.append({
            "product_id": r.product_id,
            "name": p.name if p else "",
            "article": p.article if p else "",
            "quantity": r.qty,
            "revenue": r.rev,
        })
    return {"data": out}


@router.get("/purchases")
def purchases_report(
    date_from: str | None = None,
    date_to: str | None = None,
    format: str = Query("json", pattern=r"^(json|xlsx)$"),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "warehouse"])),
):
    q = db.query(models.Purchase).filter(models.Purchase.status == models.DocumentStatus.posted)
    if date_from:
        q = q.filter(models.Purchase.date >= date_from)
    if date_to:
        q = q.filter(models.Purchase.date <= date_to)
    rows = []
    for p in q.order_by(models.Purchase.date.desc()).all():
        for item in p.items:
            rows.append({
                "number": p.number,
                "date": p.date.strftime("%Y-%m-%d %H:%M:%S") if p.date else "",
                "supplier": p.supplier.name if p.supplier else "",
                "product": item.product.name if item.product else "",
                "quantity": item.quantity,
                "price": item.price,
                "amount": item.amount,
            })
    if format == "json":
        return {"data": rows}
    return _to_excel(rows, "purchases_report.xlsx")
