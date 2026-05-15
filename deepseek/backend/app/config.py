import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Enamelware Trade Accounting System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./db/warehouse.db")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 2

    DEFAULT_MIN_STOCK: int = 10
    COMPANY_NAME: str = "ООО ЭмальПром"
    COMPANY_INN: str = ""
    COMPANY_KPP: str = ""
    COMPANY_ADDRESS: str = ""
    COMPANY_PHONE: str = ""
    COMPANY_EMAIL: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
