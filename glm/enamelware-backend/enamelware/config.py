import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Enamelware Accounting"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = "super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    DATABASE_URL: str = "sqlite:///./enamelware.db"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(__file__), "uploads")
    MIN_STOCK_DEFAULT: int = 10
    COMPANY_NAME: str = "ООО \"Эмальпосуда\""
    COMPANY_INN: str = ""
    COMPANY_ADDRESS: str = ""
    COMPANY_PHONE: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()