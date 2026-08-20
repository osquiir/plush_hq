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
from models.file import ProjectFile


def check_project_files():

    with app.app_context():

        files = (
            ProjectFile.query
            .order_by(
                ProjectFile.id.asc()
            )
            .all()
        )

        print()
        print("Project files:")
        print()

        if not files:
            print("No project files found.")
            return

        for file in files:

            print(
                f"ID: {file.id}"
            )

            print(
                f"Name: {file.file_name}"
            )

            print(
                f"URL: {file.file_url}"
            )

            print(
                "-" * 40
            )


if __name__ == "__main__":
    check_project_files()