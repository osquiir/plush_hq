from datetime import datetime

from . import db


class AdCampaign(db.Model):
    __tablename__ = "ad_campaigns"

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

    platform = db.Column(
        db.String(50),
        nullable=False,
    )

    campaign_name = db.Column(
        db.String(200),
        nullable=False,
    )

    budget = db.Column(
        db.Float,
        nullable=True,
    )

    start_date = db.Column(
        db.Date,
        nullable=True,
    )

    end_date = db.Column(
        db.Date,
        nullable=True,
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="planned",
        index=True,
    )

    notes = db.Column(
        db.Text,
        nullable=True,
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
            f"<AdCampaign "
            f"{self.campaign_name}>"
        )