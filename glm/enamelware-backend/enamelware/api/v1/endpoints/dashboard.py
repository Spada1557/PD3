from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from enamelware.database import get_db
from enamelware.models import (
    Sale, SaleItem, Purchase, PurchaseItem, Product, Stock,
    Category, Notification
)
from enamelware.schemas import (
    DashboardStats, DashboardSalesChart, DashboardCategoryChart,
    TopProduct, LowStockProduct
)
from enamelware.auth import get_current_user
from enamelware.models import User
from enamelware.enums import DocumentStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    if date_from:
        start_date = datetime.fromisoformat(date_from.replace("Z", ""))
    else:
        start_date = now - timedelta(days=30)

    if date_to:
        end_date = datetime.fromisoformat(date_to.replace("Z", ""))
    else:
        end_date = now

    posted_sales = db.query(Sale).filter(
        Sale.status == DocumentStatus.posted,
        Sale.date >= start_date,
        Sale.date <= end_date,
    ).all()

    revenue = sum(s.total_amount for s in posted_sales)
    cost = sum(s.cost_amount for s in posted_sales)
    profit = revenue - cost

    stocks = db.query(Stock).all()
    stock_value = sum(s.quantity * s.avg_cost for s in stocks)

    prev_start = start_date - (end_date - start_date)
    prev_end = start_date
    prev_sales = db.query(Sale).filter(
        Sale.status == DocumentStatus.posted,
        Sale.date >= prev_start,
        Sale.date < prev_end,
    ).all()
    prev_revenue = sum(s.total_amount for s in prev_sales)
    prev_cost = sum(s.cost_amount for s in prev_sales)
    prev_profit = prev_revenue - prev_cost

    def pct_change(curr, prev):
        if prev == 0:
            return 0.0
        return round(((curr - prev) / prev) * 100, 2)

    orders_count = len(posted_sales)

    return DashboardStats(
        revenue=round(revenue, 2),
        cost=round(cost, 2),
        profit=round(profit, 2),
        stock_value=round(stock_value, 2),
        orders_count=orders_count,
        revenue_change=pct_change(revenue, prev_revenue),
        cost_change=pct_change(cost, prev_cost),
        profit_change=pct_change(profit, prev_profit),
        stock_change=0.0,
    )


@router.get("/sales-chart", response_model=DashboardSalesChart)
def sales_chart(
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    start_date = datetime.fromisoformat(date_from.replace("Z", "")) if date_from else now - timedelta(days=30)
    end_date = datetime.fromisoformat(date_to.replace("Z", "")) if date_to else now

    posted_sales = db.query(Sale).filter(
        Sale.status == DocumentStatus.posted,
        Sale.date >= start_date,
        Sale.date <= end_date,
    ).all()

    daily = {}
    current = start_date.replace(hour=0, minute=0, second=0)
    while current <= end_date:
        key = current.strftime("%Y-%m-%d")
        daily[key] = {"revenue": 0.0, "cost": 0.0, "profit": 0.0}
        current += timedelta(days=1)

    for s in posted_sales:
        key = s.date.strftime("%Y-%m-%d")
        if key in daily:
            daily[key]["revenue"] += s.total_amount
            daily[key]["cost"] += s.cost_amount
            daily[key]["profit"] += s.profit_amount

    return DashboardSalesChart(
        labels=list(daily.keys()),
        revenue=[round(v["revenue"], 2) for v in daily.values()],
        cost=[round(v["cost"], 2) for v in daily.values()],
        profit=[round(v["profit"], 2) for v in daily.values()],
    )


@router.get("/category-chart", response_model=DashboardCategoryChart)
def category_chart(
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    start_date = datetime.fromisoformat(date_from.replace("Z", "")) if date_from else now - timedelta(days=30)
    end_date = datetime.fromisoformat(date_to.replace("Z", "")) if date_to else now

    posted_sales = db.query(Sale).filter(
        Sale.status == DocumentStatus.posted,
        Sale.date >= start_date,
        Sale.date <= end_date,
    ).all()

    sale_ids = [s.id for s in posted_sales]
    items = db.query(SaleItem).filter(SaleItem.sale_id.in_(sale_ids)).all() if sale_ids else []

    category_totals = {}
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product and product.category_id:
            cat = db.query(Category).filter(Category.id == product.category_id).first()
            name = cat.name if cat else "Без категории"
        else:
            name = "Без категории"
        category_totals[name] = category_totals.get(name, 0) + item.amount

    return DashboardCategoryChart(
        labels=list(category_totals.keys()),
        values=[round(v, 2) for v in category_totals.values()],
    )


@router.get("/top-products", response_model=list[TopProduct])
def top_products(
    limit: int = Query(5, ge=1, le=20),
    date_from: str = None,
    date_to: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    start_date = datetime.fromisoformat(date_from.replace("Z", "")) if date_from else now - timedelta(days=30)
    end_date = datetime.fromisoformat(date_to.replace("Z", "")) if date_to else now

    posted_sales = db.query(Sale).filter(
        Sale.status == DocumentStatus.posted,
        Sale.date >= start_date,
        Sale.date <= end_date,
    ).all()

    sale_ids = [s.id for s in posted_sales]
    items = db.query(SaleItem).filter(SaleItem.sale_id.in_(sale_ids)).all() if sale_ids else []

    product_totals = {}
    for item in items:
        if item.product_id not in product_totals:
            product_totals[item.product_id] = {"value": 0.0, "quantity": 0.0}
        product_totals[item.product_id]["value"] += item.amount
        product_totals[item.product_id]["quantity"] += item.quantity

    sorted_products = sorted(product_totals.items(), key=lambda x: x[1]["value"], reverse=True)[:limit]
    result = []
    for pid, vals in sorted_products:
        product = db.query(Product).filter(Product.id == pid).first()
        if product:
            result.append(TopProduct(id=pid, name=product.name, article=product.article, value=round(vals["value"], 2), quantity=round(vals["quantity"], 2)))
    return result


@router.get("/low-stock", response_model=list[LowStockProduct])
def low_stock_products(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stocks = db.query(Stock).all()
    result = []
    for s in stocks:
        product = db.query(Product).filter(Product.id == s.product_id).first()
        if product and s.quantity < product.min_stock:
            result.append(LowStockProduct(
                id=product.id, name=product.name, article=product.article,
                quantity=s.quantity, min_stock=product.min_stock,
            ))
    result.sort(key=lambda x: (x.min_stock - x.quantity), reverse=True)
    return result[:5]


@router.get("/unread-count")
def unread_notifications_count(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).count()
    return {"count": count}