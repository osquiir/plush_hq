import os
import sys

from sqlalchemy import (
    MetaData,
    create_engine,
    inspect,
    select,
    text,
)


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(
        0,
        PROJECT_ROOT,
    )


# =========================================================
# IMPORT FLASK APP
# =========================================================

from app import app
from models import db


# =========================================================
# SQLITE SOURCE
# =========================================================

SQLITE_PATH = os.path.join(
    PROJECT_ROOT,
    "instance",
    "plush_platform.db",
)

SQLITE_URL = (
    "sqlite:///"
    + SQLITE_PATH.replace("\\", "/")
)


# =========================================================
# MIGRATION
# =========================================================

def migrate():

    print()
    print("=" * 60)
    print("PLUSH DATABASE MIGRATION")
    print("SQLite -> Supabase PostgreSQL")
    print("=" * 60)
    print()

    print("Source:")
    print(SQLITE_PATH)
    print()

    if not os.path.exists(SQLITE_PATH):
        print("ERROR: SQLite database not found.")
        return


    # -----------------------------------------------------
    # CONFIRMATION
    # -----------------------------------------------------

    confirmation = input(
        "Type MIGRATE to begin: "
    ).strip()

    if confirmation != "MIGRATE":
        print()
        print("Migration cancelled.")
        return


    # -----------------------------------------------------
    # SQLITE ENGINE
    # -----------------------------------------------------

    sqlite_engine = create_engine(
        SQLITE_URL
    )

    sqlite_metadata = MetaData()

    sqlite_metadata.reflect(
        bind=sqlite_engine
    )


    # -----------------------------------------------------
    # POSTGRES TARGET
    # -----------------------------------------------------

    with app.app_context():

        postgres_engine = db.engine

        postgres_inspector = inspect(
            postgres_engine
        )


        # -------------------------------------------------
        # VERIFY TARGET IS EMPTY
        # -------------------------------------------------

        print()
        print("Checking Supabase...")
        print()

        cloud_total = 0

        cloud_tables = (
            postgres_inspector
            .get_table_names(
                schema="public"
            )
        )

        with postgres_engine.connect() as connection:

            for table_name in cloud_tables:

                result = connection.execute(
                    text(
                        f'SELECT COUNT(*) '
                        f'FROM public."{table_name}"'
                    )
                )

                count = result.scalar()

                cloud_total += count


        if cloud_total != 0:

            print(
                "ERROR: Supabase is not empty."
            )

            print(
                f"Found {cloud_total} existing records."
            )

            print(
                "Migration stopped to prevent duplicates."
            )

            return


        print(
            "Supabase is empty. Migration can continue."
        )

        print()


        # -------------------------------------------------
        # DETERMINE TABLE ORDER
        # -------------------------------------------------

        migration_tables = []

        for model_table in db.metadata.sorted_tables:

            table_name = model_table.name

            if (
                table_name
                in sqlite_metadata.tables
            ):

                migration_tables.append(
                    table_name
                )


        print("Migration order:")
        print()

        for table_name in migration_tables:
            print(
                f"  - {table_name}"
            )

        print()


        # -------------------------------------------------
        # MIGRATE
        # -------------------------------------------------

        migrated_counts = {}

        try:

            with sqlite_engine.connect() as source_connection:

                with postgres_engine.begin() as target_connection:

                    for table_name in migration_tables:

                        source_table = (
                            sqlite_metadata.tables[
                                table_name
                            ]
                        )

                        target_table = (
                            db.metadata.tables[
                                table_name
                            ]
                        )


                        # ---------------------------------
                        # READ SQLITE
                        # ---------------------------------

                        result = (
                            source_connection
                            .execute(
                                select(
                                    source_table
                                )
                            )
                        )

                        rows = [
                            dict(row._mapping)
                            for row in result
                        ]


                        print(
                            f"Migrating "
                            f"{table_name:<25} "
                            f"{len(rows):>4} records"
                        )


                        # ---------------------------------
                        # INSERT POSTGRES
                        # ---------------------------------

                        if rows:

                            target_columns = {
                                column.name
                                for column
                                in target_table.columns
                            }

                            clean_rows = []

                            for row in rows:

                                clean_row = {
                                    key: value
                                    for key, value
                                    in row.items()
                                    if key
                                    in target_columns
                                }

                                clean_rows.append(
                                    clean_row
                                )


                            target_connection.execute(
                                target_table.insert(),
                                clean_rows,
                            )


                        migrated_counts[
                            table_name
                        ] = len(rows)


                    # -------------------------------------
                    # RESET POSTGRES SEQUENCES
                    # -------------------------------------

                    print()
                    print(
                        "Updating PostgreSQL sequences..."
                    )
                    print()


                    for table_name in migration_tables:

                        target_table = (
                            db.metadata.tables[
                                table_name
                            ]
                        )

                        if "id" not in target_table.columns:
                            continue


                        sequence_result = (
                            target_connection.execute(
                                text(
                                    """
                                    SELECT pg_get_serial_sequence(
                                        :table_name,
                                        'id'
                                    )
                                    """
                                ),
                                {
                                    "table_name":
                                        f"public.{table_name}"
                                },
                            )
                        )

                        sequence_name = (
                            sequence_result.scalar()
                        )


                        if not sequence_name:
                            continue


                        max_result = (
                            target_connection.execute(
                                text(
                                    f'''
                                    SELECT MAX(id)
                                    FROM public."{table_name}"
                                    '''
                                )
                            )
                        )

                        max_id = (
                            max_result.scalar()
                        )


                        if max_id is not None:

                            target_connection.execute(
                                text(
                                    """
                                    SELECT setval(
                                        :sequence_name,
                                        :max_id,
                                        true
                                    )
                                    """
                                ),
                                {
                                    "sequence_name":
                                        sequence_name,
                                    "max_id":
                                        max_id,
                                },
                            )


        except Exception as error:

            print()
            print("=" * 60)
            print("MIGRATION FAILED")
            print("=" * 60)
            print()

            print(error)
            print()

            print(
                "The PostgreSQL transaction "
                "was rolled back."
            )

            print(
                "Your SQLite database was "
                "not modified."
            )

            return


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print()
        print("=" * 60)
        print("MIGRATION COMPLETE")
        print("=" * 60)
        print()

        total = 0

        for table_name in migration_tables:

            count = migrated_counts.get(
                table_name,
                0,
            )

            total += count

            print(
                f"{table_name:<25} "
                f"{count:>6} records"
            )


        print()
        print("-" * 40)

        print(
            f"{'TOTAL':<25} "
            f"{total:>6} records"
        )

        print("-" * 40)
        print()


if __name__ == "__main__":
    migrate()