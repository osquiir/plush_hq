from datetime import datetime

from . import db


class Release(db.Model):
    __tablename__ = "releases"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey("artists.id"),
        nullable=False,
        index=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    release_type = db.Column(
        db.String(50),
        nullable=True,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="planning",
        index=True,
    )

    release_date = db.Column(
        db.Date,
        nullable=True,
        index=True,
    )

    budget = db.Column(
        db.Float,
        nullable=True,
    )

    current_stage = db.Column(
        db.String(120),
        nullable=True,
    )

    progress = db.Column(
        db.Integer,
        nullable=False,
        default=0,
    )

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

    tasks = db.relationship(
        "Task",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
    )

    files = db.relationship(
        "ProjectFile",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
    )

    notes = db.relationship(
        "Note",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
    )

    song_metadata = db.relationship(
        "SongMetadata",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan",
    )

    deal = db.relationship(
        "Deal",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan",
    )

    marketing_plan = db.relationship(
        "MarketingPlan",
        backref="release",
        uselist=False,
        cascade="all, delete-orphan",
    )

    activities = db.relationship(
        "Activity",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Activity.created_at.desc()",
    )

    comments = db.relationship(
        "Comment",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="Comment.created_at.desc()",
    )

    calendar_events = db.relationship(
        "CalendarEvent",
        backref="release",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Release {self.title}>"