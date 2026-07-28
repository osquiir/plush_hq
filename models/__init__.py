from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .artist import Artist
from .release import Release
from .task import Task
from .file import ProjectFile
from .note import Note
from .metadata import SongMetadata
from .deal import Deal
from .marketing import MarketingPlan