import os
import sqlite3


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

SQLITE_PATH = os.path.join(
    PROJECT_ROOT,
    "instance",
    "plush_platform.db",
)


def check_database():

    print()
    print("SQLite database:")
    print(SQLITE_PATH)
    print()

    if not os.path.exists(SQLITE_PATH):
        print("ERROR: SQLite database not found.")
        return

    connection = sqlite3.connect(
        SQLITE_PATH
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )

    tables = [
        row[0]
        for row in cursor.fetchall()
    ]

    print("Existing tables:")
    print()

    total_records = 0

    for table in tables:

        cursor.execute(
            f'SELECT COUNT(*) FROM "{table}"'
        )

        count = cursor.fetchone()[0]

        total_records += count

        print(
            f"{table:<25} {count:>6} records"
        )

    print()
    print("-" * 40)

    print(
        f"{'TOTAL':<25} "
        f"{total_records:>6} records"
    )

    print("-" * 40)
    print()

    connection.close()


if __name__ == "__main__":
    check_database()