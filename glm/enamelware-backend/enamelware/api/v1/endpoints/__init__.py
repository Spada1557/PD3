from enamelware.api.v1.endpoints.auth import router as auth_router
from enamelware.api.v1.endpoints.auth import router_users as auth_users_router
from enamelware.api.v1.endpoints.categories import router as categories_router
from enamelware.api.v1.endpoints.units import router as units_router
from enamelware.api.v1.endpoints.warehouses import router as warehouses_router
from enamelware.api.v1.endpoints.products import router as products_router
from enamelware.api.v1.endpoints.suppliers import router as suppliers_router
from enamelware.api.v1.endpoints.clients import router as clients_router
from enamelware.api.v1.endpoints.stock import router as stock_router
from enamelware.api.v1.endpoints.purchases import router as purchases_router
from enamelware.api.v1.endpoints.sales import router as sales_router
from enamelware.api.v1.endpoints.dashboard import router as dashboard_router
from enamelware.api.v1.endpoints.reports import router as reports_router
from enamelware.api.v1.endpoints.settings import router as settings_router
from enamelware.api.v1.endpoints.settings import router_import

__all__ = [
    "auth_router", "auth_users_router", "categories_router", "units_router",
    "warehouses_router", "products_router", "suppliers_router", "clients_router",
    "stock_router", "purchases_router", "sales_router", "dashboard_router",
    "reports_router", "settings_router", "router_import",
]