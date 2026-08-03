from datetime import datetime

from . import db


class TemplateLink(db.Model):
    __tablename__ = "template_links"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False,
    )

    category = db.Column(
        db.String(80),
        nullable=False,
        default="general",
    )

    url = db.Column(
        db.String(500),
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )