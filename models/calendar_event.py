from datetime import datetime

from . import db


class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)

    release_id = db.Column(
        db.Integer,
        db.ForeignKey("releases.id"),
        nullable=True,
        index=True,
    )

    assigned_to = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    title = db.Column(
        db.String(200),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    event_date = db.Column(
        db.DateTime,
        nullable=False,
        index=True,
    )

    event_type = db.Column(
        db.String(50),
        nullable=False,
        default="deadline",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )