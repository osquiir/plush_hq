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
from models.ad_campaign import AdCampaign


def create_ads_table():

    with app.app_context():

        print()
        print("Creating ad_campaigns table...")
        print()

        AdCampaign.__table__.create(
            bind=db.engine,
            checkfirst=True,
        )

        print(
            "ad_campaigns table created successfully."
        )

        print()


if __name__ == "__main__":
    create_ads_table()