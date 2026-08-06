from datetime import datetime

from . import db


class ProjectFile(db.Model):
    __tablename__ = "project_files"

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

    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    file_name = db.Column(
        db.String(255),
        nullable=False,
    )

    file_type = db.Column(
        db.String(100),
        nullable=True,
    )

    file_url = db.Column(
        db.String(500),
        nullable=False,
    )

    category = db.Column(
        db.String(80),
        nullable=False,
        default="other",
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

    def __repr__(self):
        return f"<ProjectFile {self.file_name}>"