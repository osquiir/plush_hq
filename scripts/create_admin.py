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


def make_admin():
    with app.app_context():

        email = input(
            "Enter the email of the user to make admin: "
        ).strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            print("User not found.")
            return

        print()
        print("User found:")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Current role: {user.role}")
        print()

        confirm = input(
            "Change this user to admin? (y/n): "
        ).strip().lower()

        if confirm != "y":
            print("Cancelled.")
            return

        user.role = "admin"

        db.session.commit()

        print()
        print("User updated successfully.")
        print(f"{user.email} is now an admin.")


if __name__ == "__main__":
    make_admin()