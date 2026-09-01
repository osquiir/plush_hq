import os
from datetime import date, datetime
from uuid import uuid4
from dotenv import load_dotenv
from supabase import create_client

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    current_user,
    login_required,
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
from models.ad_campaign import AdCampaign

load_dotenv()


SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_SECRET_KEY = os.getenv(
    "SUPABASE_SECRET_KEY"
)

SUPABASE_BUCKET = os.getenv(
    "SUPABASE_BUCKET"
)


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_SECRET_KEY,
)

releases_bp = Blueprint(
    "releases",
    __name__,
)


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


# =========================================================
# HELPERS
# =========================================================
def get_ingestion_readiness(release_record):

    files = release_record.files

    metadata = release_record.song_metadata


    # ---------------------------------------------
    # SINGLE ART
    # ---------------------------------------------

    single_art_ready = any(
        project_file.category
        in {
            "single_art",
            "artwork",
        }
        for project_file in files
    )


    # ---------------------------------------------
    # MASTERED AUDIO
    # ---------------------------------------------

    master_audio_ready = any(
        project_file.category
        in {
            "master_audio",
            "audio",
        }
        for project_file in files
    )


    # ---------------------------------------------
    # METADATA
    # ---------------------------------------------

    metadata_ready = (
        metadata is not None
        and bool(
            metadata.song_title
            and metadata.song_title.strip()
        )
    )


    # ---------------------------------------------
    # LYRICS
    # ---------------------------------------------

    lyrics_ready = (
        metadata is not None
        and bool(
            metadata.lyrics
            and metadata.lyrics.strip()
        )
    )


    assets = [
        {
            "name": "Single Art",
            "ready": single_art_ready,
        },
        {
            "name": "Mastered Audio",
            "ready": master_audio_ready,
        },
        {
            "name": "Metadata Information",
            "ready": metadata_ready,
        },
        {
            "name": "Lyrics",
            "ready": lyrics_ready,
        },
    ]


    completed = sum(
        1
        for asset in assets
        if asset["ready"]
    )

    total = len(assets)

    progress = round(
        completed / total * 100
    )


    return {
        "assets": assets,
        "completed": completed,
        "total": total,
        "progress": progress,
        "ready": completed == total,
    }

def sync_required_asset_task(
    release_record,
    category,
    completed,
):

    task_map = {
        "single_art": "Artwork created/approved",
        "master_audio": "Master delivered",
    }

    task_name = task_map.get(
        category
    )

    # This category is not connected
    # to a workflow task.
    if not task_name:
        return

    task = (
        Task.query
        .filter_by(
            release_id=release_record.id,
            task_name=task_name,
        )
        .first()
    )

    if not task:
        return

    if completed:

        task.status = "done"

        task.completed_at = (
            datetime.utcnow()
        )

    else:

        task.status = "todo"
        task.completed_at = None


def recalculate_release_progress(
    release_record,
):

    total_tasks = len(
        release_record.tasks
    )

    completed_tasks = sum(
        1
        for task in release_record.tasks
        if task.status == "done"
    )

    release_record.progress = (
        round(
            completed_tasks
            / total_tasks
            * 100
        )
        if total_tasks
        else 0
    )


    pending_tasks = [
        task
        for task in release_record.tasks
        if task.status != "done"
    ]


    if pending_tasks:

        release_record.current_stage = (
            pending_tasks[0].task_name
        )

        if (
            release_record.status
            == "completed"
        ):

            release_record.status = (
                "planning"
            )

    else:

        release_record.current_stage = (
            "Completed"
        )

        release_record.status = (
            "completed"
        )

def get_media_signed_url(storage_path):

    if not storage_path:
        return None

    try:

        response = (
            supabase
            .storage
            .from_(SUPABASE_BUCKET)
            .create_signed_url(
                storage_path,
                3600,
            )
        )

        return (
            response.get("signedURL")
            or response.get("signedUrl")
            or response.get("signed_url")
        )

    except Exception as error:

        print(
            "Failed to create signed URL:",
            error,
        )

        return None
    
def artist_can_access_release(release_record):

    if not current_user.is_artist():
        return True

    if current_user.artist_id is None:
        return False

    return (
        release_record.artist_id
        == current_user.artist_id
    )


def block_artist_edit(release_record):

    if not current_user.is_artist():
        return None

    flash(
        "Artist accounts have view-only access.",
        "danger",
    )

    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
    )


# =========================================================
# RELEASE LIST
# =========================================================

@releases_bp.route("/releases")
@login_required
def releases():

    if current_user.is_artist():

        if current_user.artist_id is None:

            all_releases = []

        else:

            all_releases = (
                Release.query
                .filter(
                    Release.artist_id
                    == current_user.artist_id
                )
                .order_by(
                    Release.release_date.asc()
                )
                .all()
            )

    else:

        all_releases = (
            Release.query
            .order_by(
                Release.release_date.asc()
            )
            .all()
        )

    return render_template(
        "releases.html",
        releases=all_releases,
    )


# =========================================================
# CREATE RELEASE
# =========================================================

@releases_bp.route(
    "/releases/new",
    methods=["GET", "POST"],
)
@login_required
def create_release():

    if current_user.is_artist():

        flash(
            "Artist accounts have view-only access.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )

    if request.method == "POST":

        artist_name = request.form.get(
            "artist_name",
            "",
        ).strip()

        artist_email = request.form.get(
            "artist_email",
            "",
        ).strip()

        title = request.form.get(
            "title",
            "",
        ).strip()

        release_type = request.form.get(
            "release_type",
            "",
        ).strip()

        release_date_value = request.form.get(
            "release_date",
            "",
        ).strip()

        budget_value = request.form.get(
            "budget",
            "",
        ).strip()

        current_stage = request.form.get(
            "current_stage",
            "",
        ).strip()


        if not artist_name or not title:

            flash(
                "Artist name and release title are required.",
                "danger",
            )

            return render_template(
                "new_release.html"
            )


        parsed_release_date = None

        if release_date_value:

            try:

                parsed_release_date = (
                    date.fromisoformat(
                        release_date_value
                    )
                )

            except ValueError:

                flash(
                    "The release date is invalid.",
                    "danger",
                )

                return render_template(
                    "new_release.html"
                )


        parsed_budget = None

        if budget_value:

            try:

                parsed_budget = float(
                    budget_value
                )

            except ValueError:

                flash(
                    "The budget must be a valid number.",
                    "danger",
                )

                return render_template(
                    "new_release.html"
                )


        artist = (
            Artist.query
            .filter(
                db.func.lower(
                    Artist.name
                )
                == artist_name.lower()
            )
            .first()
        )


        if artist is None:

            artist = Artist(
                name=artist_name,
                email=(
                    artist_email
                    or None
                ),
            )

            db.session.add(
                artist
            )

            db.session.flush()


        new_release = Release(
            artist_id=artist.id,
            title=title,
            release_type=(
                release_type
                or "Single"
            ),
            status="planning",
            release_date=parsed_release_date,
            budget=parsed_budget,
            current_stage=(
                current_stage
                or "Deal signed"
            ),
            progress=0,
        )

        db.session.add(
            new_release
        )

        db.session.flush()


        for task_name in DEFAULT_WORKFLOW:

            task = Task(
                release_id=new_release.id,
                task_name=task_name,
                status="todo",
            )

            db.session.add(
                task
            )


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


    return render_template(
        "new_release.html"
    )


# =========================================================
# RELEASE DETAIL
# =========================================================

@releases_bp.route(
    "/releases/<int:release_id>"
)
@login_required
def release_detail(release_id):

    release_record = (
        Release.query.get_or_404(
            release_id
        )
    )


    # -----------------------------------------------------
    # ARTIST ACCESS CHECK
    # -----------------------------------------------------

    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    # -----------------------------------------------------
    # PROGRESS
    # -----------------------------------------------------

    completed_tasks = sum(
        1
        for task in release_record.tasks
        if task.status == "done"
    )

    total_tasks = len(
        release_record.tasks
    )

    progress = (
        round(
            (
                completed_tasks
                / total_tasks
            )
            * 100
        )
        if total_tasks
        else 0
    )


    # -----------------------------------------------------
    # RELEASE DATA
    # -----------------------------------------------------

    release = {
        "id":
            release_record.id,

        "artist":
            release_record.artist.name,

        "title":
            release_record.title,

        "type":
            release_record.release_type
            or "Single",

        "status":
            release_record.status
            .replace(
                "_",
                " ",
            )
            .title(),

        "release_date": (
            release_record.release_date
            .strftime(
                "%b %d, %Y"
            )
            if release_record.release_date
            else "Not scheduled"
        ),

        "stage":
            release_record.current_stage
            or "Not selected",

        "budget": (
            f"{release_record.budget:,.2f}"
            if release_record.budget is not None
            else "0.00"
        ),

        "progress":
            progress,
    }


    # -----------------------------------------------------
    # WORKFLOW
    # -----------------------------------------------------

    tasks = [
        {
            "id":
                task.id,

            "name":
                task.task_name,

            "status":
                task.status,

            "completed":
                task.status == "done",
        }

        for task
        in release_record.tasks
    ]


    # -----------------------------------------------------
    # MEDIA VISIBILITY
    # -----------------------------------------------------

    visible_files = (
        release_record.files
    )

    if current_user.is_artist():

        visible_files = [
            project_file
            for project_file
            in release_record.files
            if (
                project_file.visibility
                == "artist_visible"
            )
        ]


    files = [
        {
            "id":
                project_file.id,

            "name":
                project_file.file_name,

            "category": (
                project_file.category
                or "other"
            )
            .replace(
                "_",
                " ",
            )
            .title(),

            "visibility": (
                project_file.visibility
                or "internal"
            )
            .replace(
                "_",
                " ",
            )
            .title(),

            "file_type":
                project_file.file_type,

            "url":
                get_media_signed_url(
                    project_file.file_url
                ),

            "created_at":
                project_file.created_at,
        }

        for project_file
        in sorted(
            visible_files,
            key=lambda item:
                item.created_at,
            reverse=True,
        )
    ]


    # -----------------------------------------------------
    # NOTES VISIBILITY
    # -----------------------------------------------------

    visible_notes = (
        release_record.notes
    )

    if current_user.is_artist():

        visible_notes = [
            note
            for note
            in release_record.notes
            if (
                note.visibility
                == "artist_visible"
            )
        ]


    notes = [
        {
            "id":
                note.id,

            "content":
                note.content,

            "visibility":
                note.visibility
                .replace(
                    "_",
                    " ",
                )
                .title(),

            "created_at":
                note.created_at,
        }

        for note
        in sorted(
            visible_notes,
            key=lambda item:
                item.created_at,
            reverse=True,
        )
    ]


    # -----------------------------------------------------
    # AI
    # -----------------------------------------------------

    ai_summary = (
        "AI insights will appear here after the release "
        "contains enough project information."
    )


    # -----------------------------------------------------
    # TIMELINE
    # -----------------------------------------------------

    activities = []

    for activity in release_record.activities:

        user_name = "System"

        if activity.user_id:

            user = db.session.get(
                User,
                activity.user_id,
            )

            if user:
                user_name = user.name


        activities.append(
            {
                "id":
                    activity.id,

                "action":
                    activity.action,

                "entity_type":
                    activity.entity_type,

                "created_at":
                    activity.created_at,

                "user_name":
                    user_name,
            }
        )


    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    metadata_record = (
        release_record.song_metadata
    )


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


    # -----------------------------------------------------
    # INGESTION READINESS
    # -----------------------------------------------------

    ingestion = get_ingestion_readiness(
        release_record
    )


    # -----------------------------------------------------
    # AD CAMPAIGNS
    # -----------------------------------------------------

    ad_campaigns = (
        AdCampaign.query
        .filter_by(
            release_id=release_record.id
        )
        .order_by(
            AdCampaign.created_at.desc()
        )
        .all()
    )


    total_ad_budget = sum(
        campaign.budget or 0
        for campaign in ad_campaigns
    )


    # -----------------------------------------------------
    # RENDER
    # -----------------------------------------------------

    return render_template(
        "release_detail.html",
        release=release,
        tasks=tasks,
        files=files,
        notes=notes,
        activities=activities,
        metadata=metadata,
        ai_summary=ai_summary,
        ingestion=ingestion,
        ad_campaigns=ad_campaigns,
        total_ad_budget=total_ad_budget,
    )


# =========================================================
# TOGGLE WORKFLOW TASK
# =========================================================

@releases_bp.route(
    "/tasks/<int:task_id>/toggle",
    methods=["POST"],
)
@login_required
def toggle_task(task_id):

    task = Task.query.get_or_404(
        task_id
    )

    release_record = (
        task.release
    )


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    if task.status == "done":

        task.status = "todo"
        task.completed_at = None

        action = (
            f'Reopened task '
            f'"{task.task_name}"'
        )

    else:

        task.status = "done"
        task.completed_at = (
            datetime.utcnow()
        )

        action = (
            f'Completed task '
            f'"{task.task_name}"'
        )


    total_tasks = len(
        release_record.tasks
    )

    completed_tasks = sum(
        1
        for release_task
        in release_record.tasks
        if (
            release_task.status
            == "done"
        )
    )


    release_record.progress = (
        round(
            (
                completed_tasks
                / total_tasks
            )
            * 100
        )
        if total_tasks
        else 0
    )


    pending_tasks = [
        release_task
        for release_task
        in release_record.tasks
        if (
            release_task.status
            != "done"
        )
    ]


    if pending_tasks:

        release_record.current_stage = (
            pending_tasks[0]
            .task_name
        )

    else:

        release_record.current_stage = (
            "Completed"
        )

        release_record.status = (
            "completed"
        )


    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=action,
        entity_type="task",
        entity_id=task.id,
    )


    db.session.add(
        activity
    )

    db.session.commit()


    flash(
        "Workflow updated successfully.",
        "success",
    )


    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#workflow"
    )


# =========================================================
# ADD NOTE
# =========================================================

@releases_bp.route(
    "/releases/<int:release_id>/notes",
    methods=["POST"],
)
@login_required
def add_note(release_id):

    release_record = (
        Release.query.get_or_404(
            release_id
        )
    )


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    content = request.form.get(
        "content",
        "",
    ).strip()

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


    db.session.add(
        note
    )

    db.session.flush()


    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action="Added a release note",
        entity_type="note",
        entity_id=note.id,
    )


    db.session.add(
        activity
    )

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


# =========================================================
# SAVE METADATA
# =========================================================

@releases_bp.route(
    "/releases/<int:release_id>/metadata",
    methods=["POST"],
)
@login_required
def save_metadata(release_id):

    release_record = (
        Release.query.get_or_404(
            release_id
        )
    )


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    song_title = request.form.get(
        "song_title",
        "",
    ).strip()

    isrc = request.form.get(
        "isrc",
        "",
    ).strip()

    upc = request.form.get(
        "upc",
        "",
    ).strip()

    language = request.form.get(
        "language",
        "",
    ).strip()

    writers = request.form.get(
        "writers",
        "",
    ).strip()

    producers = request.form.get(
        "producers",
        "",
    ).strip()

    credits = request.form.get(
        "credits",
        "",
    ).strip()

    lyrics = request.form.get(
        "lyrics",
        "",
    ).strip()

    explicit = (
        request.form.get(
            "explicit"
        )
        == "on"
    )


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


    metadata = (
        release_record.song_metadata
    )


    if metadata is None:

        metadata = SongMetadata(
            release_id=release_record.id,
            song_title=song_title,
        )

        db.session.add(
            metadata
        )

        action = (
            "Added song metadata"
        )

    else:

        action = (
            "Updated song metadata"
        )


    metadata.song_title = (
        song_title
    )

    metadata.isrc = (
        isrc
        or None
    )

    metadata.upc = (
        upc
        or None
    )

    metadata.language = (
        language
        or None
    )

    metadata.writers = (
        writers
        or None
    )

    metadata.producers = (
        producers
        or None
    )

    metadata.credits = (
        credits
        or None
    )

    metadata.lyrics = (
        lyrics
        or None
    )

    metadata.explicit = (
        explicit
    )

    metadata_complete = all([
        metadata.song_title,
        metadata.writers,
        metadata.producers,
        metadata.language,
    ])

    metadata_task = (
        Task.query
        .filter_by(
            release_id=release_record.id,
            task_name="Song metadata completed",
        )
        .first()
    )

    if metadata_task:

        if metadata_complete:
            metadata_task.status = "done"
            metadata_task.completed_at = datetime.utcnow()

        else:
            metadata_task.status = "todo"
            metadata_task.completed_at = None


    recalculate_release_progress(
        release_record
    )


    db.session.flush()


    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=action,
        entity_type="song_metadata",
        entity_id=metadata.id,
    )


    db.session.add(
        activity
    )

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


# =========================================================
# UPLOAD MEDIA
# =========================================================

@releases_bp.route(
    "/releases/<int:release_id>/media",
    methods=["POST"],
)
@login_required
def upload_media(release_id):

    release_record = (
        Release.query.get_or_404(
            release_id
        )
    )


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    uploaded_file = (
        request.files.get(
            "media_file"
        )
    )

    category = request.form.get(
        "category",
        "other",
    ).strip()

    visibility = request.form.get(
        "visibility",
        "internal",
    ).strip()


    allowed_categories = {
        "single_art",
        "master_audio",
        "video",
        "promo",
        "document",
        "other",

        # Legacy categories
        "audio",
        "artwork",
    }


    allowed_visibilities = {
        "internal",
        "artist_visible",
    }


    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):

        flash(
            "Please select a file.",
            "danger",
        )

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


    # =========================================================
    # PREVENT DUPLICATE REQUIRED ASSETS
    # =========================================================

    if category in {
        "single_art",
        "master_audio",
    }:

        existing_asset = (
            ProjectFile.query
            .filter_by(
                release_id=release_record.id,
                category=category,
            )
            .first()
        )

        if existing_asset:

            flash(
                (
                    "This release already has "
                    f"{category.replace('_', ' ').title()}."
                ),
                "danger",
            )

            return redirect(
                url_for(
                    "releases.release_detail",
                    release_id=release_record.id,
                )
                + "#media"
            )


    original_filename = (
        secure_filename(
            uploaded_file.filename
        )
    )


    if not original_filename:

        flash(
            "The selected filename is invalid.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#media"
        )


    extension = (
        os.path.splitext(
            original_filename
        )[1]
        .lower()
    )

    stored_filename = (
        f"{uuid4().hex}"
        f"{extension}"
    )

    storage_path = (
        f"uploads/releases/"
        f"{release_record.id}/"
        f"{stored_filename}"
    )


    try:

        file_bytes = uploaded_file.read()

        upload_options = {
            "upsert": "false",
        }

        if uploaded_file.mimetype:

            upload_options[
                "content-type"
            ] = uploaded_file.mimetype


        supabase.storage.from_(
            SUPABASE_BUCKET
        ).upload(
            path=storage_path,
            file=file_bytes,
            file_options=upload_options,
        )


    except Exception as error:

        print(
            "Supabase upload failed:",
            error,
        )

        flash(
            "The file could not be uploaded.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#media"
        )


    media_record = ProjectFile(
        release_id=release_record.id,
        uploaded_by=current_user.id,
        file_name=original_filename,
        file_type=uploaded_file.mimetype,
        file_url=storage_path,
        category=category,
        visibility=visibility,
    )


    db.session.add(
        media_record
    )

    db.session.flush()


    # =========================================================
    # SYNC WORKFLOW WITH REQUIRED ASSET
    # =========================================================

    sync_required_asset_task(
        release_record,
        category,
        True,
    )


    recalculate_release_progress(
        release_record
    )


    # =========================================================
    # ACTIVITY
    # =========================================================

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


    db.session.add(
        activity
    )

    db.session.commit()


    flash(
        "Media uploaded successfully.",
        "success",
    )


    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#media"
    )


# =========================================================
# DELETE MEDIA
# =========================================================

@releases_bp.route(
    "/media/<int:file_id>/delete",
    methods=["POST"],
)
@login_required
def delete_media(file_id):

    media_record = (
        ProjectFile.query.get_or_404(
            file_id
        )
    )

    release_record = (
        media_record.release
    )


    # -----------------------------------------------------
    # RELEASE ACCESS
    # -----------------------------------------------------

    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    # -----------------------------------------------------
    # ARTISTS ARE VIEW-ONLY
    # -----------------------------------------------------

    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    file_name = (
        media_record.file_name
    )

    storage_path = (
        media_record.file_url
    )

    category = (
        media_record.category
    )


    # -----------------------------------------------------
    # DELETE FROM SUPABASE STORAGE
    # -----------------------------------------------------

    try:

        if storage_path:

            supabase.storage.from_(
                SUPABASE_BUCKET
            ).remove(
                [storage_path]
            )


    except Exception as error:

        print(
            "Supabase delete failed:",
            error,
        )

        flash(
            "The file could not be deleted from storage.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#media"
        )


    # -----------------------------------------------------
    # DELETE DATABASE RECORD
    # -----------------------------------------------------

    db.session.delete(
        media_record
    )

    db.session.flush()


    # -----------------------------------------------------
    # SYNC WORKFLOW WITH REQUIRED ASSET
    # -----------------------------------------------------

    sync_required_asset_task(
        release_record,
        category,
        False,
    )


    recalculate_release_progress(
        release_record
    )


    # -----------------------------------------------------
    # ACTIVITY
    # -----------------------------------------------------

    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=(
            f'Deleted media '
            f'"{file_name}"'
        ),
        entity_type="project_file",
        entity_id=None,
    )


    db.session.add(
        activity
    )

    db.session.commit()


    flash(
        "Media deleted successfully.",
        "success",
    )


    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#media"
    )
# =========================================================
# CREATE AD CAMPAIGN
# =========================================================

@releases_bp.route(
    "/releases/<int:release_id>/ads",
    methods=["POST"],
)
@login_required
def create_ad_campaign(release_id):

    release_record = (
        Release.query.get_or_404(
            release_id
        )
    )


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    platform = request.form.get(
        "platform",
        "",
    ).strip().lower()

    campaign_name = request.form.get(
        "campaign_name",
        "",
    ).strip()

    budget_value = request.form.get(
        "budget",
        "",
    ).strip()

    start_date_value = request.form.get(
        "start_date",
        "",
    ).strip()

    end_date_value = request.form.get(
        "end_date",
        "",
    ).strip()

    status = request.form.get(
        "status",
        "planned",
    ).strip().lower()

    notes = request.form.get(
        "notes",
        "",
    ).strip()


    allowed_platforms = {
        "meta",
        "tiktok",
        "youtube",
        "google",
        "other",
    }

    allowed_statuses = {
        "planned",
        "active",
        "completed",
    }


    if not campaign_name:

        flash(
            "Campaign name is required.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#ads"
        )


    if platform not in allowed_platforms:
        platform = "other"

    if status not in allowed_statuses:
        status = "planned"


    budget = None

    if budget_value:

        try:

            budget = float(
                budget_value
            )

        except ValueError:

            flash(
                "Budget must be a valid number.",
                "danger",
            )

            return redirect(
                url_for(
                    "releases.release_detail",
                    release_id=release_record.id,
                )
                + "#ads"
            )


    start_date = None

    if start_date_value:

        try:

            start_date = date.fromisoformat(
                start_date_value
            )

        except ValueError:

            flash(
                "Start date is invalid.",
                "danger",
            )

            return redirect(
                url_for(
                    "releases.release_detail",
                    release_id=release_record.id,
                )
                + "#ads"
            )


    end_date = None

    if end_date_value:

        try:

            end_date = date.fromisoformat(
                end_date_value
            )

        except ValueError:

            flash(
                "End date is invalid.",
                "danger",
            )

            return redirect(
                url_for(
                    "releases.release_detail",
                    release_id=release_record.id,
                )
                + "#ads"
            )


    if (
        start_date
        and end_date
        and end_date < start_date
    ):

        flash(
            "End date cannot be before the start date.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.release_detail",
                release_id=release_record.id,
            )
            + "#ads"
        )


    campaign = AdCampaign(
        release_id=release_record.id,
        platform=platform,
        campaign_name=campaign_name,
        budget=budget,
        start_date=start_date,
        end_date=end_date,
        status=status,
        notes=notes or None,
    )


    db.session.add(
        campaign
    )

    db.session.flush()


    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=(
            f'Created ad campaign '
            f'"{campaign_name}"'
        ),
        entity_type="ad_campaign",
        entity_id=campaign.id,
    )


    db.session.add(
        activity
    )

    db.session.commit()


    flash(
        "Ad campaign created successfully.",
        "success",
    )


    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#ads"
    )
# =========================================================
# DELETE AD CAMPAIGN
# =========================================================

@releases_bp.route(
    "/ads/<int:campaign_id>/delete",
    methods=["POST"],
)
@login_required
def delete_ad_campaign(campaign_id):

    campaign = (
        AdCampaign.query.get_or_404(
            campaign_id
        )
    )

    release_record = campaign.release


    if not artist_can_access_release(
        release_record
    ):

        flash(
            "You do not have permission to access this release.",
            "danger",
        )

        return redirect(
            url_for(
                "releases.releases"
            )
        )


    artist_block = block_artist_edit(
        release_record
    )

    if artist_block:
        return artist_block


    campaign_name = (
        campaign.campaign_name
    )


    db.session.delete(
        campaign
    )

    db.session.flush()


    activity = Activity(
        release_id=release_record.id,
        user_id=current_user.id,
        action=(
            f'Deleted ad campaign '
            f'"{campaign_name}"'
        ),
        entity_type="ad_campaign",
        entity_id=None,
    )

    db.session.add(
        activity
    )

    db.session.commit()


    flash(
        "Ad campaign deleted successfully.",
        "success",
    )


    return redirect(
        url_for(
            "releases.release_detail",
            release_id=release_record.id,
        )
        + "#ads"
    )