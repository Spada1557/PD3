from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import init_db, engine, Base
from app.config import settings
from app.utils.seed import seed_data

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("db", exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_data()


from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.stock import router as stock_router
from app.api.purchases import router as purchases_router
from app.api.sales import router as sales_router
from app.api.reports import router as reports_router
from app.api.categories import router as categories_router
from app.api.units import router as units_router
from app.api.warehouses import router as warehouses_router
from app.api.suppliers import router as suppliers_router
from app.api.clients import router as clients_router
from app.api.dashboard import router as dashboard_router
from app.api.notifications import router as notifications_router
from app.api.settings import router as settings_router

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(stock_router)
app.include_router(purchases_router)
app.include_router(sales_router)
app.include_router(reports_router)
app.include_router(categories_router)
app.include_router(units_router)
app.include_router(warehouses_router)
app.include_router(suppliers_router)
app.include_router(clients_router)
app.include_router(dashboard_router)
app.include_router(notifications_router)
app.include_router(settings_router)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
