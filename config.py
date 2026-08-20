import os
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv()


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")


def get_database_url():

    # If DATABASE_URL exists, use it.
    # This will be useful later in Vercel.
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    # If Supabase variables exist, build PostgreSQL URL.
    if all([
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME,
    ]):

        encoded_password = quote_plus(
            DB_PASSWORD
        )

        return (
            f"postgresql+psycopg2://"
            f"{DB_USER}:"
            f"{encoded_password}@"
            f"{DB_HOST}:"
            f"{DB_PORT}/"
            f"{DB_NAME}"
            f"?sslmode=require"
        )

    # Local fallback
    return "sqlite:///plush_platform.db"


class Config:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "dev-secret-key",
    )

    SQLALCHEMY_DATABASE_URI = (
        get_database_url()
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Important when using Supabase Transaction Pooler
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }