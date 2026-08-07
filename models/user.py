from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from . import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(120),
        nullable=False,
    )

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False,
    )

    role = db.Column(
        db.String(30),
        nullable=False,
        default="team",
    )

    artist_id = db.Column(
        db.Integer,
        db.ForeignKey("artists.id"),
        nullable=True,
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    notes = db.relationship(
        "Note",
        backref="author",
        lazy=True,
    )

    uploaded_files = db.relationship(
        "ProjectFile",
        backref="uploader",
        lazy=True,
    )

    assigned_tasks = db.relationship(
        "Task",
        backref="assignee",
        lazy=True,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password,
        )

    def is_admin(self):
        return self.role == "admin"

    def is_artist(self):
        return self.role == "artist"

    def __repr__(self):
        return f"<User {self.email}>"