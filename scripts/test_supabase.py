import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool


# Load variables from .env
load_dotenv()


# Read environment variables
USER = os.getenv("user")
RAW_PASSWORD = os.getenv("password", "")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")


# Encode special characters in the password safely
PASSWORD = quote_plus(
    RAW_PASSWORD
)


# Build PostgreSQL connection URL
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{USER}:{PASSWORD}@"
    f"{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require"
)


# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


# Test connection
try:

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.scalar()

        print()
        print("Connection successful!")
        print()
        print("PostgreSQL:")
        print(version)


except Exception as error:

    print()
    print("Connection failed.")
    print()
    print(error)