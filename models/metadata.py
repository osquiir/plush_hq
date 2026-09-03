from datetime import datetime

from . import db


class SongMetadata(db.Model):
    __tablename__ = "song_metadata"

    # =====================================================
    # PRIMARY KEY / RELATIONSHIP
    # =====================================================

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    release_id = db.Column(
        db.Integer,
        db.ForeignKey("releases.id"),
        unique=True,
        nullable=False,
        index=True,
    )


    # =====================================================
    # SONG INFORMATION
    # =====================================================

    song_title = db.Column(
        db.String(200),
        nullable=False,
    )

    main_artists = db.Column(
        db.String(500),
        nullable=True,
    )

    featured_artists = db.Column(
        db.String(500),
        nullable=True,
    )

    isrc = db.Column(
        db.String(50),
        nullable=True,
    )

    upc = db.Column(
        db.String(50),
        nullable=True,
    )

    explicit = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    language = db.Column(
        db.String(80),
        nullable=True,
    )

    p_line = db.Column(
        db.String(500),
        nullable=True,
    )

    c_line = db.Column(
        db.String(500),
        nullable=True,
    )

    apple_url = db.Column(
        db.String(500),
        nullable=True,
    )

    spotify_url = db.Column(
        db.String(500),
        nullable=True,
    )


    # =====================================================
    # RECORDING CREDITS
    # =====================================================

    producers = db.Column(
        db.Text,
        nullable=True,
    )

    executive_producer = db.Column(
        db.String(500),
        nullable=True,
    )

    vocal_production = db.Column(
        db.String(500),
        nullable=True,
    )

    recording_engineer = db.Column(
        db.String(500),
        nullable=True,
    )

    recorded_at = db.Column(
        db.String(500),
        nullable=True,
    )

    mixing_engineer = db.Column(
        db.String(500),
        nullable=True,
    )

    mixed_at = db.Column(
        db.String(500),
        nullable=True,
    )

    immersive_mixing_engineer = db.Column(
        db.String(500),
        nullable=True,
    )

    mastering_engineer = db.Column(
        db.String(500),
        nullable=True,
    )

    mastered_at = db.Column(
        db.String(500),
        nullable=True,
    )

    immersive_mastering_engineer = db.Column(
        db.String(500),
        nullable=True,
    )

    artwork_design = db.Column(
        db.String(500),
        nullable=True,
    )

    artwork_photography = db.Column(
        db.String(500),
        nullable=True,
    )


    # =====================================================
    # VIDEO CREDITS
    # =====================================================

    video_director = db.Column(
        db.String(500),
        nullable=True,
    )

    video_production_house = db.Column(
        db.String(500),
        nullable=True,
    )

    video_editor = db.Column(
        db.String(500),
        nullable=True,
    )

    color_grading = db.Column(
        db.String(500),
        nullable=True,
    )


    # =====================================================
    # LICENSING INFORMATION
    # =====================================================

    cover_recording = db.Column(
        db.Boolean,
        nullable=True,
    )

    adaptation = db.Column(
        db.Boolean,
        nullable=True,
    )

    sample = db.Column(
        db.Boolean,
        nullable=True,
    )


    # =====================================================
    # LYRICS
    # =====================================================

    lyrics = db.Column(
        db.Text,
        nullable=True,
    )


    # =====================================================
    # LEGACY FIELDS
    # =====================================================
    #
    # Keep these fields because existing Plush releases
    # may already contain data in them.
    # =====================================================

    writers = db.Column(
        db.Text,
        nullable=True,
    )

    credits = db.Column(
        db.Text,
        nullable=True,
    )


    # =====================================================
    # TIMESTAMPS
    # =====================================================

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self):
        return (
            f"<SongMetadata {self.song_title}>"
        )