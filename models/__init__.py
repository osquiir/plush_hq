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
from .activity import Activity
from .comment import Comment
from .calendar_event import CalendarEvent
from .template_link import TemplateLink