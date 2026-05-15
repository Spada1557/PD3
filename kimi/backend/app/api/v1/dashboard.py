from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from app.core.database import get_db
from app.core.security import require_role, get_current_user
from app import models, schemas
from datetime import datetime, timedelta

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _parse_date(d: str | None) -> datetime | None:
    if not d:
        return None
    return datetime.strptime(d[:10], "%Y-%m-%d")


@router.get("", response_model=schemas.DashboardData)
def dashboard(
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager"])),
):
    df = _parse_date(date_from)
    dt = _parse_date(date_to)
    if not df:
        df = datetime.now() - timedelta(days=30)
    if not dt:
        dt = datetime.now()
    dt = dt.replace(hour=23, minute=59, second=59)

    # Sales in range
    sales_q = db.query(models.Sale).filter(
        models.Sale.status == models.DocumentStatus.posted,
        models.Sale.date >= df,
        models.Sale.date <= dt,
    )
    sales = sales_q.all()
    revenue = sum(s.total_amount for s in sales)
    cost = sum(s.total_cost for s in sales)
    profit = revenue - cost
    orders_count = len(sales)

    # Previous period for %
    prev_df = df - (dt - df)
    prev_sales_q = db.query(models.Sale).filter(
        models.Sale.status == models.DocumentStatus.posted,
        models.Sale.date >= prev_df,
        models.Sale.date < df,
    )
    prev_sales = prev_sales_q.all()
    prev_revenue = sum(s.total_amount for s in prev_sales)
    prev_profit = sum(s.total_amount - s.total_cost for s in prev_sales)
    revenue_change = round(((revenue - prev_revenue) / prev_revenue) * 100, 2) if prev_revenue else 0.0
    profit_change = round(((profit - prev_profit) / prev_profit) * 100, 2) if prev_profit else 0.0

    # Stock value
    stock_value = db.query(func.sum(models.Stock.quantity * models.Stock.avg_cost)).scalar() or 0.0

    # Sales chart points (daily)
    chart = {}
    for s in sales:
        d = s.date.strftime("%Y-%m-%d")
        if d not in chart:
            chart[d] = {"revenue": 0.0, "cost": 0.0, "profit": 0.0}
        chart[d]["revenue"] += s.total_amount
        chart[d]["cost"] += s.total_cost
        chart[d]["profit"] += s.total_amount - s.total_cost
    sales_chart = [schemas.DashboardSalePoint(date=k, revenue=v["revenue"], cost=v["cost"], profit=v["profit"]) for k, v in sorted(chart.items())]

    # Categories chart
    cat_map = {}
    for s in sales:
        for item in s.items:
            cat = item.product.category.name if (item.product and item.product.category) else "Без категории"
            cat_map.setdefault(cat, 0.0)
            cat_map[cat] += item.amount
    categories_chart = [schemas.DashboardCategorySlice(category=k, revenue=v) for k, v in cat_map.items()]

    # Top-5 products
    prod_map = {}
    for s in sales:
        for item in s.items:
            pid = item.product_id
            if pid not in prod_map:
                prod_map[pid] = {"name": item.product.name if item.product else "", "article": item.product.article if item.product else "", "revenue": 0.0, "quantity": 0.0}
            prod_map[pid]["revenue"] += item.amount
            prod_map[pid]["quantity"] += item.quantity
    top_products = sorted(prod_map.values(), key=lambda x: x["revenue"], reverse=True)[:5]
    top_products = [schemas.TopProduct(product_id=k, **v) for k, v in list(prod_map.items())[:5]]

    # Top-5 documents
    top_docs = sorted(sales, key=lambda x: x.total_amount, reverse=True)[:5]
    top_documents = [schemas.TopDocument(
        document_id=s.id,
        number=s.number,
        total_amount=s.total_amount,
        date=s.date.strftime("%Y-%m-%d") if s.date else "",
    ) for s in top_docs]

    # Low stock
    low = db.query(models.Stock).filter(models.Stock.quantity <= models.Product.min_stock).join(models.Product).all()
    low_stock = [schemas.LowStockItem(
        product_id=s.product_id,
        name=s.product.name if s.product else "",
        article=s.product.article if s.product else "",
        quantity=s.quantity,
        min_stock=s.product.min_stock if s.product else 0,
    ) for s in low[:5]]

    summary = schemas.DashboardSummary(
        revenue=round(revenue, 2),
        cost=round(cost, 2),
        profit=round(profit, 2),
        stock_value=round(stock_value, 2),
        orders_count=orders_count,
        revenue_change_percent=revenue_change,
        profit_change_percent=profit_change,
    )
    result = schemas.DashboardData(
        summary=summary,
        sales_chart=sales_chart,
        categories_chart=categories_chart,
        top_products=top_products,
        top_documents=top_documents,
        low_stock=low_stock,
    )
    return jsonable_encoder(result)


@router.get("/notifications", response_model=list[schemas.NotificationOut])
def notifications(
    db: Session = Depends(get_db),
    user: models.User = Depends(require_role(["admin", "manager", "warehouse"])),
):
    out = []
    low = db.query(models.Stock).filter(models.Stock.quantity <= models.Product.min_stock).join(models.Product).all()
    for idx, s in enumerate(low, start=1):
        out.append(schemas.NotificationOut(
            id=idx,
            title="Низкий остаток",
            message=f"{s.product.name} ({s.product.article}) — остаток {s.quantity}, мин. {s.product.min_stock}",
            type="low_stock",
            is_read=False,
            created_at=datetime.utcnow(),
        ))
    return out
