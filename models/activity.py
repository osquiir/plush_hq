from datetime import datetime

from . import db


class Activity(db.Model):
    __tablename__ = "activities"

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

    action = db.Column(
        db.String(255),
        nullable=False,
    )

    entity_type = db.Column(
        db.String(50),
        nullable=True,
    )

    entity_id = db.Column(
        db.Integer,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    # SOLO esta relación
    user = db.relationship(
        "User",
        backref="activities",
    )