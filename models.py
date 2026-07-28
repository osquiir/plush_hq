from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False, default="team")  # admin, team, artist
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship("Note", backref="author", lazy=True)
    uploaded_files = db.relationship("ProjectFile", backref="uploader", lazy=True)
    assigned_tasks = db.relationship("Task", backref="assignee", lazy=True)


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    genre = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), nullable=True)
    instagram_url = db.Column(db.String(255), nullable=True)
    spotify_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship("Project", backref="artist", lazy=True)
    users = db.relationship("User", backref="artist", lazy=True)


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("artists.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="planning")
    release_date = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    current_stage = db.Column(db.String(120), nullable=True)
    progress = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship("Task", backref="project", lazy=True, cascade="all, delete-orphan")
    files = db.relationship("ProjectFile", backref="project", lazy=True, cascade="all, delete-orphan")
    notes = db.relationship("Note", backref="project", lazy=True, cascade="all, delete-orphan")
    song_metadata = db.relationship("SongMetadata", backref="project", uselist=False, cascade="all, delete-orphan")
    deal = db.relationship("Deal", backref="project", uselist=False, cascade="all, delete-orphan")
    marketing_plan = db.relationship("MarketingPlan", backref="project", uselist=False, cascade="all, delete-orphan")


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="todo")  # todo, in_progress, done
    due_date = db.Column(db.Date, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ProjectFile(db.Model):
    __tablename__ = "project_files"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(100), nullable=True)
    file_url = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(80), nullable=True)  # audio, artwork, contract, lyrics, marketing, other
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    content = db.Column(db.Text, nullable=False)
    visibility = db.Column(db.String(50), default="internal")  # internal, artist_visible
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SongMetadata(db.Model):
    __tablename__ = "song_metadata"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
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


class Deal(db.Model):
    __tablename__ = "deals"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
    deal_type = db.Column(db.String(100), nullable=True)
    advance_amount = db.Column(db.Float, nullable=True)
    royalty_split = db.Column(db.String(100), nullable=True)
    marketing_budget = db.Column(db.Float, nullable=True)
    contract_signed = db.Column(db.Boolean, default=False)
    contract_file_id = db.Column(db.Integer, db.ForeignKey("project_files.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MarketingPlan(db.Model):
    __tablename__ = "marketing_plans"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=True, nullable=False)
    paid_ads_budget = db.Column(db.Float, nullable=True)
    organic_strategy = db.Column(db.Text, nullable=True)
    content_schedule = db.Column(db.Text, nullable=True)
    playlist_pitching_status = db.Column(db.String(100), nullable=True)
    rollout_plan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)