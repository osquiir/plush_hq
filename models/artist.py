from datetime import datetime

from . import db


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    genre = db.Column(
        db.String(100),
        nullable=True,
    )

    email = db.Column(
        db.String(150),
        nullable=True,
    )

    instagram_url = db.Column(
        db.String(255),
        nullable=True,
    )

    spotify_url = db.Column(
        db.String(255),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
    )

    releases = db.relationship(
        "Release",
        backref="artist",
        lazy=True,
        cascade="all, delete-orphan",
    )

    users = db.relationship(
        "User",
        backref="artist",
        lazy=True,
    )