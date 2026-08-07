from datetime import date, timedelta

from flask import Blueprint, render_template

from models.activity import Activity
from models.release import Release

from flask_login import login_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
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

        days_until_release = None

        if release.release_date:
            days_until_release = (
                release.release_date - today
            ).days

        total_tasks = len(release.tasks)

        completed_tasks = sum(
            1
            for task in release.tasks
            if task.status == "done"
        )

        health = "Healthy"
        health_class = "success"

        if (
            days_until_release is not None
            and 0 <= days_until_release <= 3
            and release.progress < 50
        ):
            health = "Blocked"
            health_class = "danger"

        elif (
            release.progress < 40
            or (
                days_until_release is not None
                and 0 <= days_until_release <= 7
                and release.progress < 70
            )
        ):
            health = "At Risk"
            health_class = "warning"

        release_rows.append(
            {
                "id": release.id,
                "artist": release.artist.name,
                "title": release.title,
                "stage": (
                    release.current_stage
                    or "Not selected"
                ),
                "release_date": (
                    release.release_date.strftime(
                        "%b %d, %Y"
                    )
                    if release.release_date
                    else "Not scheduled"
                ),
                "progress": release.progress,
                "status": release.status.replace(
                    "_",
                    " ",
                ).title(),
                "health": health,
                "health_class": health_class,
                "completed_tasks": completed_tasks,
                "total_tasks": total_tasks,
                "releasing_soon": (
                    release.release_date is not None
                    and today
                    <= release.release_date
                    <= next_week
                ),
            }
        )

    priorities = []

    for release in active_releases:

        incomplete_tasks = [
            task
            for task in release.tasks
            if task.status != "done"
        ]

        days_until_release = None

        if release.release_date:
            days_until_release = (
                release.release_date - today
            ).days

        if (
            days_until_release is not None
            and 0 <= days_until_release <= 3
            and release.progress < 50
        ):
            priorities.append(
                {
                    "release_id": release.id,
                    "artist": release.artist.name,
                    "release": release.title,
                    "message": (
                        f"Release is in "
                        f"{days_until_release} day(s) "
                        f"and only "
                        f"{release.progress}% complete."
                    ),
                    "level": "High",
                }
            )

            continue

        if incomplete_tasks:

            next_task = incomplete_tasks[0]

            priorities.append(
                {
                    "release_id": release.id,
                    "artist": release.artist.name,
                    "release": release.title,
                    "message": (
                        f"Next step: "
                        f"{next_task.task_name}"
                    ),
                    "level": (
                        "High"
                        if release.progress < 30
                        else "Pending"
                    ),
                }
            )

    priorities = priorities[:5]

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

    recent_releases = (
        Release.query
        .order_by(Release.updated_at.desc())
        .limit(5)
        .all()
    )

    recent_release_rows = [
        {
            "id": release.id,
            "artist": release.artist.name,
            "title": release.title,
            "progress": release.progress,
            "stage": (
                release.current_stage
                or "Not selected"
            ),
            "updated_at": release.updated_at,
        }
        for release in recent_releases
    ]

    upcoming_releases = (
        Release.query
        .filter(
            Release.release_date.isnot(None),
            Release.release_date >= today,
            Release.status != "completed",
        )
        .order_by(Release.release_date.asc())
        .limit(5)
        .all()
    )

    upcoming_release_rows = [
        {
            "id": release.id,
            "artist": release.artist.name,
            "title": release.title,
            "release_date": release.release_date,
            "progress": release.progress,
        }
        for release in upcoming_releases
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
        recent_releases=recent_release_rows,
        upcoming_releases=upcoming_release_rows,
    )