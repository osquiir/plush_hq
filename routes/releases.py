from datetime import date, datetime

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from models import db
from models.artist import Artist
from models.release import Release
from models.task import Task
from models.activity import Activity
from models.note import Note


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
            "name": project_file.file_name,
            "category": (
                project_file.category or "Other"
            ),
        }
        for project_file in release_record.files
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

    activities = [
        {
            "id": activity.id,
            "action": activity.action,
            "entity_type": activity.entity_type,
            "created_at": activity.created_at,
        }
        for activity in release_record.activities
    ]

    return render_template(
        "release_detail.html",
        release=release,
        tasks=tasks,
        files=files,
        notes=notes,
        activities=activities,
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
        user_id=None,
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
        user_id=None,
        content=content,
        visibility=visibility,
    )

    db.session.add(note)
    db.session.flush()

    activity = Activity(
        release_id=release_record.id,
        user_id=None,
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