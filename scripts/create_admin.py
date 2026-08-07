import os
import sys

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import app
from models import db
from models.user import User


def create_admin():
    with app.app_context():

        existing = User.query.filter_by(
            email="admin@plush.com"
        ).first()

        if existing:
            print("Admin already exists.")
            return

        admin = User(
            name="Plush Admin",
            email="admin@plush.com",
            role="admin",
        )

        admin.set_password("ChangeMe123!")

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully.")
        print("Email: admin@plush.com")
        print("Password: ChangeMe123!")


if __name__ == "__main__":
    create_admin()