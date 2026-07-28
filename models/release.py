from datetime import datetime
from . import db


class Release(db.Model):
    __tablename__ = "releases"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer,
        db.ForeignKey("artists.id"),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    release_type = db.Column(db.String(50), nullable=True)
    status = db.Column(
        db.String(50),
        nullable=False,
        default="planning"
    )

    release_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    current_stage = db.Column(db.String(120), nullable=True)
    progress = db.Column(db.Integer, nullable=False, default=0)

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    tasks = db.relationship(
        "Task",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan"
    )

    files = db.relationship(
        "ProjectFile",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan"
    )

    notes = db.relationship(
        "Note",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan"
    )

    song_metadata = db.relationship(
        "SongMetadata",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan"
    )

    deal = db.relationship(
        "Deal",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan"
    )

    marketing_plan = db.relationship(
        "MarketingPlan",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan"
    )