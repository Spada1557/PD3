from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func as sa_func, extract
from app.database import get_db
from app.models import Sale, SaleItem, Product, Category, Stock, Purchase
from app.schemas import DashboardResponse
from app.api.deps import get_current_user
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("")
def get_dashboard(
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    now = datetime.utcnow()
    current_start = date_from or (now - timedelta(days=30)).strftime("%Y-%m-%d")
    current_end_raw = date_to or now.strftime("%Y-%m-%d")

    current_dt_from = datetime.fromisoformat(current_start)
    current_dt_to = datetime.fromisoformat(current_end_raw)
    if not date_to:
        current_dt_to = current_dt_to.replace(hour=23, minute=59, second=59)

    # Current period stats
    current_sales = db.query(
        sa_func.coalesce(sa_func.sum(Sale.total_amount), 0),
        sa_func.coalesce(sa_func.sum(Sale.total_cost), 0),
        sa_func.coalesce(sa_func.sum(Sale.total_profit), 0),
        sa_func.count(Sale.id),
    ).filter(
        Sale.status == "posted",
        Sale.date >= current_dt_from,
        Sale.date <= current_dt_to,
    ).first()

    revenue = round(current_sales[0] or 0, 2)
    cost = round(current_sales[1] or 0, 2)
    profit = round(current_sales[2] or 0, 2)
    orders_count = current_sales[3] or 0

    # Previous period for comparison
    period_days = (current_dt_to - current_dt_from).days or 30
    prev_end = current_dt_from - timedelta(days=1)
    prev_start = prev_end - timedelta(days=period_days)

    prev_sales = db.query(
        sa_func.coalesce(sa_func.sum(Sale.total_amount), 0),
        sa_func.coalesce(sa_func.sum(Sale.total_cost), 0),
        sa_func.coalesce(sa_func.sum(Sale.total_profit), 0),
        sa_func.count(Sale.id),
    ).filter(
        Sale.status == "posted",
        Sale.date >= prev_start,
        Sale.date <= prev_end,
    ).first()

    prev_revenue = prev_sales[0] or 0
    prev_cost = prev_sales[1] or 0
    prev_profit = prev_sales[2] or 0
    prev_orders = prev_sales[3] or 0

    def pct_change(current, previous):
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return round((current - previous) / previous * 100, 1)

    # Stock summary
    stock_data = db.query(
        sa_func.count(Stock.id),
        sa_func.coalesce(sa_func.sum(Stock.quantity * Stock.avg_cost), 0),
    ).first()
    stock_count = stock_data[0] or 0
    stock_value = round(stock_data[1] or 0, 2)

    # Sales chart (daily)
    sales_chart = []
    for i in range(30):
        day = current_dt_to - timedelta(days=29 - i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        day_sales = db.query(
            sa_func.coalesce(sa_func.sum(Sale.total_amount), 0),
        ).filter(
            Sale.status == "posted",
            Sale.date >= day_start,
            Sale.date <= day_end,
        ).first()
        sales_chart.append({
            "date": day_start.strftime("%d.%m"),
            "amount": round(day_sales[0] or 0, 2),
        })

    # Category distribution
    cat_data = db.query(
        Category.name,
        sa_func.coalesce(sa_func.sum(SaleItem.amount), 0),
    ).join(SaleItem.product).join(Product.category).join(Sale).filter(
        Sale.status == "posted",
        Sale.date >= current_dt_from,
        Sale.date <= current_dt_to,
    ).group_by(Category.name).all()

    cat_total = sum(d[1] for d in cat_data) or 1
    category_distribution = [
        {"name": d[0], "amount": round(d[1], 2), "percent": round(d[1] / cat_total * 100, 1)}
        for d in cat_data
    ]

    # Top 5 products
    top_products_q = db.query(
        SaleItem.product_id,
        Product.name,
        sa_func.sum(SaleItem.amount).label("revenue"),
        sa_func.sum(SaleItem.quantity).label("qty"),
    ).join(Sale).join(Product).filter(
        Sale.status == "posted",
        Sale.date >= current_dt_from,
        Sale.date <= current_dt_to,
    ).group_by(SaleItem.product_id).order_by(sa_func.sum(SaleItem.amount).desc()).limit(5).all()

    top_products = [{"name": p.name, "revenue": round(p.revenue, 2), "quantity": round(p.qty, 2)} for p in top_products_q]

    # Top 5 documents
    top_docs = db.query(
        Sale.number,
        Sale.total_amount,
        Sale.client_id,
    ).filter(
        Sale.status == "posted",
        Sale.date >= current_dt_from,
        Sale.date <= current_dt_to,
    ).order_by(Sale.total_amount.desc()).limit(5).all()

    from app.models import Client
    top_documents = []
    for d in top_docs:
        client = db.query(Client).filter(Client.id == d.client_id).first()
        top_documents.append({
            "number": d.number,
            "amount": d.total_amount,
            "client": client.name if client else "",
        })

    # Low stock
    low_stock_q = db.query(Stock, Product).join(Product).filter(
        Stock.quantity <= Product.min_stock,
    ).order_by(Stock.quantity).limit(5).all()

    low_stock = [{
        "name": p.name,
        "article": p.article,
        "quantity": s.quantity,
        "min_stock": p.min_stock,
    } for s, p in low_stock_q]

    return DashboardResponse(
        revenue=revenue,
        revenue_change=pct_change(revenue, prev_revenue),
        cost=cost,
        cost_change=pct_change(cost, prev_cost),
        profit=profit,
        profit_change=pct_change(profit, prev_profit),
        stock_count=stock_count,
        stock_value=stock_value,
        orders_count=orders_count,
        orders_change=pct_change(orders_count, prev_orders),
        sales_chart=sales_chart,
        category_distribution=category_distribution,
        top_products=top_products,
        top_documents=top_documents,
        low_stock=low_stock,
    )
