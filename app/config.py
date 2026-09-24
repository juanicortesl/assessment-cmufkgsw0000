import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = os.getenv("APP_ENV", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local.db")

    VENDOR_SHARED_API_KEY: str = os.getenv(
        "VENDOR_SHARED_API_KEY",
        "ld_vendor_shared_live_99f8a2130e4c7b",
    )
    VENDOR_SHARED_SECRET: str = os.getenv(
        "VENDOR_SHARED_SECRET",
        "sec_ld_s3_shared_vault_token_2024",
    )

    NOTARY_PARTNER_API_URL: str = os.getenv(
        "NOTARY_PARTNER_API_URL",
        "https://api.valida-notaria-externa.cl/v1/certify",
    )
    NOTARY_PARTNER_TIMEOUT_SECONDS: int = int(
        os.getenv("NOTARY_PARTNER_TIMEOUT_SECONDS", "30")
    )


settings = Settings()
