from datetime import datetime
from . import db


class SongMetadata(db.Model):
    __tablename__ = "song_metadata"

    id = db.Column(db.Integer, primary_key=True)
    release_id = db.Column(db.Integer, db.ForeignKey("releases.id"), unique=True, nullable=False)
    song_title = db.Column(db.String(200), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    credits = db.Column(db.Text, nullable=True)
    isrc = db.Column(db.String(50), nullable=True)
    upc = db.Column(db.String(50), nullable=True)
    writers = db.Column(db.Text, nullable=True)
    producers = db.Column(db.Text, nullable=True)
    explicit = db.Column(db.Boolean, default=False)
    language = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)