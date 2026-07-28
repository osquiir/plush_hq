from datetime import datetime
from . import db


class MarketingPlan(db.Model):
    __tablename__ = "marketing_plans"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("releases.id"), unique=True, nullable=False)
    paid_ads_budget = db.Column(db.Float, nullable=True)
    organic_strategy = db.Column(db.Text, nullable=True)
    content_schedule = db.Column(db.Text, nullable=True)
    playlist_pitching_status = db.Column(db.String(100), nullable=True)
    rollout_plan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)