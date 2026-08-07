import os
from datetime import date, datetime
from uuid import uuid4
from flask_login import (
    current_user,
    login_required,
)


from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from models import db
from models.activity import Activity
from models.artist import Artist
from models.file import ProjectFile
from models.metadata import SongMetadata
from models.note import Note
from models.release import Release
from models.task import Task
from models.user import User

releases_bp = Blueprint("releases", __name__)


DEFAULT_WORKFLOW = [
    "Deal signed",
    "Producer agreement signed",
    "Marketing ideation",
    "Team intro/meeting",
    "Artwork agreement signed",
    "Master delivered",
    "Song metadata completed",
    "Artwork created/approved",
    "Spotify canvas approved",
    "Marketing budget agreed upon for paid ads",
    "Rollout plan developed",
    "Song ingestion",
    "Playlist pitching",
    "Release date confirmed",
    "Marketing efforts - paid and organic",
]


@releases_bp.route("/releases")
def releases():
    all_releases = (
        Release.query
        .order_by(Release.release_date.asc())
        .all()
    )

    return render_template(
        "releases.html",
        releases=all_releases,
    )


@releases_bp.route("/releases/new", methods=["GET", "POST"])
def create_release():
    if request.method == "POST":
        artist_name = request.form.get("artist_name", "").strip()
        artist_email = request.form.get("artist_email", "").strip()
        title = request.form.get("title", "").strip()
        release_type = request.form.get("release_type", "").strip()
        release_date_value = request.form.get("release_date", "").strip()
        budget_value = request.form.get("budget", "").strip()
        current_stage = request.form.get("current_stage", "").strip()

        if not artist_name or not title:
            flash(
                "Artist name and release title are required.",
                "danger",
            )
            return render_template("new_release.html")

        parsed_release_date = None

        if release_date_value:
            try:
                parsed_release_date = date.fromisoformat(
                    release_date_value
                )
            except ValueError:
                flash("The release date is invalid.", "danger")
                return render_template("new_release.html")

        parsed_budget = None

        if budget_value:
            try:
                parsed_budget = float(budget_value)
            except ValueError:
                flash("The budget must be a valid number.", "danger")
                return render_template("new_release.html")

        artist = Artist.query.filter(
            db.func.lower(Artist.name) == artist_name.lower()
        ).first()

        if artist is None:
            artist = Artist(
                name=artist_name,
                email=artist_email or None,
            )
            db.session.add(artist)
            db.session.flush()

        new_release = Release(
            artist_id=artist.id,
            title=title,
            release_type=release_type or "Single",
            status="planning",
            release_date=parsed_release_date,
            budget=parsed_budget,
            current_stage=current_stage or "Deal signed",
            progress=0,
        )

        db.session.add(new_release)
        db.session.flush()

        for task_name in DEFAULT_WORKFLOW:
            task = Task(
                release_id=new_release.id,
                task_name=task_name,
                status="todo",
            )
            db.session.add(task)

        db.session.commit()

        flash(
            "The release was created successfully.",
            "success",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=new_release.id,
            )
        )

    return render_template("new_release.html")


@releases_bp.route("/releases/<int:release_id>")

def release_detail(release_id):
    release_record = Release.query.get_or_404(release_id)

    completed_tasks = sum(
        1 for task in release_record.tasks
        if task.status == "done"
    )

    total_tasks = len(release_record.tasks)

    progress = (
        round((completed_tasks / total_tasks) * 100)
        if total_tasks
        else 0
    )

    release = {
        "id": release_record.id,
        "artist": release_record.artist.name,
        "title": release_record.title,
        "type": release_record.release_type or "Single",
        "status": release_record.status.replace("_", " ").title(),
        "release_date": (
            release_record.release_date.strftime("%b %d, %Y")
            if release_record.release_date
            else "Not scheduled"
        ),
        "stage": (
            release_record.current_stage
            or "Not selected"
        ),
        "budget": (
            f"{release_record.budget:,.2f}"
            if release_record.budget is not None
            else "0.00"
        ),
        "progress": progress,
    }

    tasks = [
        {
            "id": task.id,
            "name": task.task_name,
            "status": task.status,
            "completed": task.status == "done",
        }
        for task in release_record.tasks
    ]

    files = [
        {
            "id": project_file.id,
            "name": project_file.file_name,
            "category": (
                project_file.category or "other"
            ).replace("_", " ").title(),
            "visibility": (
                project_file.visibility or "internal"
            ).replace("_", " ").title(),
            "file_type": project_file.file_type,
            "url": url_for(
                "static",
                filename=project_file.file_url,
            ),
            "created_at": project_file.created_at,
        }
        for project_file in sorted(
            release_record.files,
            key=lambda item: item.created_at,
            reverse=True,
        )
    ]

    notes = [
        {
            "id": note.id,
            "content": note.content,
            "visibility": note.visibility.replace(
                "_",
                " ",
            ).title(),
            "created_at": note.created_at,
        }
        for note in sorted(
            release_record.notes,
            key=lambda item: item.created_at,
            reverse=True,
        )
    ]

    ai_summary = (
        "AI insights will appear here after the release "
        "contains enough project information."
    )

    activities = []

    for activity in release_record.activities:

        user_name = "System"

        if activity.user_id:

            user = User.query.get(activity.user_id)

            if user:
                user_name = user.name

        activities.append(
            {
                "id": activity.id,
                "action": activity.action,
                "entity_type": activity.entity_type,
                "created_at": activity.created_at,
                "user_name": user_name,
            }
        )
    metadata_record = release_record.song_metadata

    metadata = {
        "song_title": (
            metadata_record.song_title
            if metadata_record
            else release_record.title
        ),
        "isrc": (
            metadata_record.isrc
            if metadata_record
            else ""
        ),
        "upc": (
            metadata_record.upc
            if metadata_record
            else ""
        ),
        "language": (
            metadata_record.language
            if metadata_record
            else ""
        ),
        "writers": (
            metadata_record.writers
            if metadata_record
            else ""
        ),
        "producers": (
            metadata_record.producers
            if metadata_record
            else ""
        ),
        "credits": (
            metadata_record.credits
            if metadata_record
            else ""
        ),
        "lyrics": (
            metadata_record.lyrics
            if metadata_record
            else ""
        ),
        "explicit": (
            metadata_record.explicit
            if metadata_record
            else False
        ),
    }

    return render_template(
        "release_detail.html",
        release=release,
        tasks=tasks,
        files=files,
        notes=notes,
        activities=activities,
        metadata=metadata,
        ai_summary=ai_summary,
    )


@releases_bp.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    release_record = task.release

    if task.status == "done":
        task.status = "todo"
        task.completed_at = None
        action = f'Reopened task "{task.task_name}"'
    else:
        task.status = "done"
        task.completed_at = datetime.utcnow()
        action = f'Completed task "{task.task_name}"'

    total_tasks = len(release_record.tasks)
    completed_tasks = sum(
        1
        for release_task in release_record.tasks
        if release_task.status == "done"
    )

    release_record.progress = (
        round((completed_tasks / total_tasks) * 100)
        if total_tasks
        else 0
    )

    pending_tasks = [
        release_task
        for release_task in release_record.tasks
        if release_task.status != "done"
    ]

    if pending_tasks:
        release_record.current_stage = pending_tasks[0].task_name
    else:
        release_record.current_stage = "Completed"
        release_record.status = "completed"

    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=action,
        entity_type="task",
        entity_id=task.id,
    )

    db.session.add(activity)
    db.session.commit()

    flash("Workflow updated successfully.", "success")

    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#workflow"
    )

@releases_bp.route(
    "/releases/<int:release_id>/notes",
    methods=["POST"],
)
def add_note(release_id):
    release_record = Release.query.get_or_404(release_id)

    content = request.form.get("content", "").strip()
    visibility = request.form.get(
        "visibility",
        "internal",
    ).strip()

    allowed_visibilities = {
        "internal",
        "artist_visible",
    }

    if not content:
        flash(
            "The note cannot be empty.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#notes"
        )

    if visibility not in allowed_visibilities:
        visibility = "internal"

    note = Note(
        release_id=release_record.id,
        user_id=current_user.id,
        content=content,
        visibility=visibility,
    )

    db.session.add(note)
    db.session.flush()

    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action="Added a release note",
        entity_type="note",
        entity_id=note.id,
    )

    db.session.add(activity)
    db.session.commit()

    flash(
        "Note added successfully.",
        "success",
    )

    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#notes"
    )

@releases_bp.route(
    "/releases/<int:release_id>/metadata",
    methods=["POST"],
)
def save_metadata(release_id):
    release_record = Release.query.get_or_404(release_id)

    song_title = request.form.get("song_title", "").strip()
    isrc = request.form.get("isrc", "").strip()
    upc = request.form.get("upc", "").strip()
    language = request.form.get("language", "").strip()
    writers = request.form.get("writers", "").strip()
    producers = request.form.get("producers", "").strip()
    credits = request.form.get("credits", "").strip()
    lyrics = request.form.get("lyrics", "").strip()
    explicit = request.form.get("explicit") == "on"

    if not song_title:
        flash(
            "Song title is required.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#metadata"
        )

    metadata = release_record.song_metadata

    if metadata is None:
        metadata = SongMetadata(
            release_id=release_record.id,
            song_title=song_title,
        )
        db.session.add(metadata)
        action = "Added song metadata"
    else:
        action = "Updated song metadata"

    metadata.song_title = song_title
    metadata.isrc = isrc or None
    metadata.upc = upc or None
    metadata.language = language or None
    metadata.writers = writers or None
    metadata.producers = producers or None
    metadata.credits = credits or None
    metadata.lyrics = lyrics or None
    metadata.explicit = explicit

    db.session.flush()

    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=action,
        entity_type="song_metadata",
        entity_id=metadata.id,
    )

    db.session.add(activity)
    db.session.commit()

    flash(
        "Song metadata saved successfully.",
        "success",
    )

    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#metadata"
    )
@releases_bp.route(
    "/releases/<int:release_id>/media",
    methods=["POST"],
)
def upload_media(release_id):
    release_record = Release.query.get_or_404(release_id)

    uploaded_file = request.files.get("media_file")
    category = request.form.get("category", "other").strip()
    visibility = request.form.get("visibility", "internal").strip()

    allowed_categories = {
        "audio",
        "artwork",
        "video",
        "other",
    }

    allowed_visibilities = {
        "internal",
        "artist_visible",
    }

    if uploaded_file is None or uploaded_file.filename == "":
        flash("Please select a file.", "danger")
        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#media"
        )

    if category not in allowed_categories:
        category = "other"

    if visibility not in allowed_visibilities:
        visibility = "internal"

    original_filename = secure_filename(uploaded_file.filename)

    if not original_filename:
        flash("The selected filename is invalid.", "danger")
        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#media"
        )

    extension = os.path.splitext(original_filename)[1].lower()
    stored_filename = f"{uuid4().hex}{extension}"

    upload_folder = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "releases",
        str(release_record.id),
    )

    os.makedirs(upload_folder, exist_ok=True)

    file_path = os.path.join(
        upload_folder,
        stored_filename,
    )

    uploaded_file.save(file_path)

    relative_url = (
        f"uploads/releases/"
        f"{release_record.id}/"
        f"{stored_filename}"
    )

    media_record = ProjectFile(
        release_id=release_record.id,
        uploaded_by=current_user.id,
        file_name=original_filename,
        file_type=uploaded_file.mimetype,
        file_url=relative_url,
        category=category,
        visibility=visibility,
    )

    db.session.add(media_record)
    db.session.flush()

    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=(
            f'Uploaded media '
            f'"{original_filename}"'
        ),
        entity_type="project_file",
        entity_id=media_record.id,
    )

    db.session.add(activity)
    db.session.commit()

    flash("Media uploaded successfully.", "success")

    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#media"
    )

