from datetime import datetime
from . import db


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, db.ForeignKey("releases.id"), unique=True, nullable=False)
    deal_type = db.Column(db.String(100), nullable=True)
    advance_amount = db.Column(db.Float, nullable=True)
    royalty_split = db.Column(db.String(100), nullable=True)
    marketing_budget = db.Column(db.Float, nullable=True)
    contract_signed = db.Column(db.Boolean, default=False)
    contract_file_id = db.Column(db.Integer, db.ForeignKey("project_files.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)