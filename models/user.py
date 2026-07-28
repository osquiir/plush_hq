from datetime import datetime
from . import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="team")
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship("Note", backref="author", lazy=True)
    uploaded_files = db.relationship("ProjectFile", backref="uploader", lazy=True)
    assigned_tasks = db.relationship("Task", backref="assignee", lazy=True)