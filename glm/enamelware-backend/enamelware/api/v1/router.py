from fastapi import APIRouter
from enamelware.api.v1.endpoints import (
    auth, categories, units, warehouses, products, suppliers,
    clients, stock, purchases, sales, dashboard, reports, settings
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(auth.router_users)

api_router.include_router(categories.router)
api_router.include_router(units.router)
api_router.include_router(warehouses.router)
api_router.include_router(products.router)
api_router.include_router(suppliers.router)
api_router.include_router(clients.router)
api_router.include_router(stock.router)
api_router.include_router(purchases.router)
api_router.include_router(sales.router)
api_router.include_router(dashboard.router)
api_router.include_router(reports.router)
api_router.include_router(settings.router)
api_router.include_router(settings.router_import)