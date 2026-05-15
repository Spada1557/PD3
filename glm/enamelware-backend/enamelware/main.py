from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from enamelware.config import settings
from enamelware.database import init_db, get_db
from enamelware.seed import seed_database
from enamelware.api.v1.router import api_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Система учёта товарооборота для производства эмалированной посуды",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "server_error", "message": str(exc)},
    )


app.include_router(api_router)

upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.on_event("startup")
def startup():
    init_db()
    db = next(get_db())
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("enamelware.main:app", host="0.0.0.0", port=8000, reload=True)