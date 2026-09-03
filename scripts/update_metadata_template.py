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
from models.release_writer import ReleaseWriter


METADATA_COLUMNS = [

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS main_artists VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS featured_artists VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS p_line VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS c_line VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS apple_url VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS spotify_url VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS executive_producer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS vocal_production VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS recording_engineer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS recorded_at VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS mixing_engineer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS mixed_at VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS immersive_mixing_engineer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS mastering_engineer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS mastered_at VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS immersive_mastering_engineer VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS artwork_design VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS artwork_photography VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS video_director VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS video_production_house VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS video_editor VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS color_grading VARCHAR(500);
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS cover_recording BOOLEAN;
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS adaptation BOOLEAN;
    """,

    """
    ALTER TABLE song_metadata
    ADD COLUMN IF NOT EXISTS sample BOOLEAN;
    """,
]


def update_metadata_template():

    with app.app_context():

        print()
        print("Updating Metadata template...")
        print()

        try:

            for statement in METADATA_COLUMNS:

                db.session.execute(
                    db.text(statement)
                )

            db.session.commit()


            ReleaseWriter.__table__.create(
                bind=db.engine,
                checkfirst=True,
            )


            print(
                "Metadata template updated successfully."
            )

            print(
                "release_writers table created successfully."
            )

            print()

        except Exception as error:

            db.session.rollback()

            print()
            print("Metadata update failed.")
            print(error)
            print()


if __name__ == "__main__":
    update_metadata_template()