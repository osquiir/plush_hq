import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool


load_dotenv()


USER = os.getenv("user")
PASSWORD = quote_plus(
    os.getenv("password", "")
)
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")


DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{USER}:{PASSWORD}@"
    f"{HOST}:{PORT}/{DBNAME}"
    f"?sslmode=require"
)


engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
)


def check_cloud_database():

    print()
    print("Supabase PostgreSQL")
    print()

    inspector = inspect(engine)

    tables = sorted(
        inspector.get_table_names(
            schema="public"
        )
    )

    total_records = 0

    with engine.connect() as connection:

        for table in tables:

            result = connection.execute(
                text(
                    f'SELECT COUNT(*) '
                    f'FROM public."{table}"'
                )
            )

            count = result.scalar()

            total_records += count

            print(
                f"{table:<25} "
                f"{count:>6} records"
            )


    print()
    print("-" * 40)

    print(
        f"{'TOTAL':<25} "
        f"{total_records:>6} records"
    )

    print("-" * 40)
    print()


if __name__ == "__main__":
    check_cloud_database()