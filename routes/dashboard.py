from datetime import date, timedelta

from flask import Blueprint, render_template

from models.activity import Activity
from models.release import Release
from models.task import Task


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    today = date.today()
    next_week = today + timedelta(days=7)

    releases = (
        Release.query
        .order_by(Release.release_date.asc())
        .all()
    )

    active_releases = [
        release
        for release in releases
        if release.status != "completed"
    ]

    on_track_count = sum(
        1
        for release in active_releases
        if release.progress >= 50
        and release.current_stage != "Completed"
    )

    needs_attention_count = sum(
        1
        for release in active_releases
        if release.progress < 50
    )

    releasing_soon_count = sum(
        1
        for release in active_releases
        if release.release_date
        and today <= release.release_date <= next_week
    )

    release_rows = []

    for release in active_releases:
        release_rows.append(
            {
                "id": release.id,
                "artist": release.artist.name,
                "title": release.title,
                "stage": release.current_stage or "Not selected",
                "release_date": (
                    release.release_date.strftime("%b %d, %Y")
                    if release.release_date
                    else "Not scheduled"
                ),
                "progress": release.progress,
                "status": release.status.replace("_", " ").title(),
            }
        )

    pending_tasks = (
        Task.query
        .filter(Task.status != "done")
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    priorities = [
        {
            "release_id": task.release_id,
            "artist": task.release.artist.name,
            "release": task.release.title,
            "message": task.task_name,
            "level": (
                "High"
                if task.due_date and task.due_date < today
                else "Pending"
            ),
        }
        for task in pending_tasks
    ]

    recent_activities = (
        Activity.query
        .order_by(Activity.created_at.desc())
        .limit(8)
        .all()
    )

    activities = [
        {
            "release_id": activity.release_id,
            "release_title": activity.release.title,
            "action": activity.action,
            "created_at": activity.created_at,
        }
        for activity in recent_activities
    ]

    return render_template(
        "dashboard.html",
        active_count=len(active_releases),
        on_track_count=on_track_count,
        needs_attention_count=needs_attention_count,
        releasing_soon_count=releasing_soon_count,
        releases=release_rows,
        priorities=priorities,
        activities=activities,
    )