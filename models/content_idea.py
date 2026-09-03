from datetime import datetime

from . import db


class ContentIdea(db.Model):
    __tablename__ = "content_ideas"

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

    channel_group = db.Column(
        db.String(50),
        nullable=False,
        default="main",
        index=True,
    )

    category = db.Column(
        db.String(100),
        nullable=True,
    )

    concept = db.Column(
        db.Text,
        nullable=False,
    )

    reference_url = db.Column(
        db.String(500),
        nullable=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="idea",
        index=True,
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

    def __repr__(self):
        return (
            f"<ContentIdea {self.id}: {self.concept[:40]}>"
        )