from fastapi import APIRouter

from . import auth, users, references, products, stock, purchases, sales, dashboard, reports, settings

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(users.router)
router.include_router(references.router)
router.include_router(products.router)
router.include_router(stock.router)
router.include_router(purchases.router)
router.include_router(sales.router)
router.include_router(dashboard.router)
router.include_router(reports.router)
router.include_router(settings.router)
