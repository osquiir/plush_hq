import os
import sys


# =========================================================
# PROJECT ROOT
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
# IMPORT APP
# =========================================================

from app import app
from models import db


# =========================================================
# DATABASE CHANGES
# =========================================================

ALTER_STATEMENTS = [
    """
    ALTER TABLE artists
    ADD COLUMN IF NOT EXISTS tiktok_url VARCHAR(255);
    """,

    """
    ALTER TABLE artists
    ADD COLUMN IF NOT EXISTS youtube_url VARCHAR(255);
    """,

    """
    ALTER TABLE artists
    ADD COLUMN IF NOT EXISTS image_url VARCHAR(500);
    """,
]


# =========================================================
# UPDATE
# =========================================================

def update_artist_columns():

    with app.app_context():

        print()
        print("Updating artists table...")
        print()

        for statement in ALTER_STATEMENTS:

            db.session.execute(
                db.text(statement)
            )

        db.session.commit()

        print(
            "Artist columns added successfully."
        )

        print()


if __name__ == "__main__":
    update_artist_columns()