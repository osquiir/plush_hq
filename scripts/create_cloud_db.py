import os
import sys


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


from app import app
from models import db


def create_cloud_database():

    with app.app_context():

        print()
        print("Creating tables in PostgreSQL...")
        print()

        db.create_all()

        print("Cloud database tables created successfully.")
        print()


if __name__ == "__main__":
    create_cloud_database()