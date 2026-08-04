from datetime import datetime

from . import db


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    release_id = db.Column(
        db.Integer,
        db.ForeignKey("releases.id"),
        nullable=False,
        index=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    content = db.Column(
        db.Text,
        nullable=False,
    )

    visibility = db.Column(
        db.String(50),
        nullable=False,
        default="internal",
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )