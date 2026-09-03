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
from models.content_idea import ContentIdea


def create_content_ideas_table():

    with app.app_context():

        print()
        print("Creating content_ideas table...")
        print()

        ContentIdea.__table__.create(
            bind=db.engine,
            checkfirst=True,
        )

        print(
            "content_ideas table created successfully."
        )

        print()


if __name__ == "__main__":
    create_content_ideas_table()