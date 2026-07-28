from flask import Blueprint, render_template

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():
    releases = [
        {
            "id": 1,
            "artist": "Mia Rose",
            "title": "After Hours",
            "stage": "Artwork Approval",
            "release_date": "Aug 02",
            "progress": 60,
            "status": "Needs Attention",
            "status_class": "warning",
        },
        {
            "id": 2,
            "artist": "Kairo",
            "title": "Late Night Drive",
            "stage": "Marketing Rollout",
            "release_date": "Jul 26",
            "progress": 80,
            "status": "On Track",
            "status_class": "good",
        },
        {
            "id": 3,
            "artist": "Luna Vega",
            "title": "Blue Moon",
            "stage": "Metadata",
            "release_date": "Aug 15",
            "progress": 45,
            "status": "In Progress",
            "status_class": "neutral",
        },
    ]

    priorities = [
        {
            "level": "High",
            "artist": "Mia Rose",
            "message": "Artwork approval is overdue.",
            "class_name": "danger",
        },
        {
            "level": "Medium",
            "artist": "Luna Vega",
            "message": "Song metadata is incomplete.",
            "class_name": "warning",
        },
        {
            "level": "Ready",
            "artist": "Kairo",
            "message": "Release is ready for the next stage.",
            "class_name": "success",
        },
    ]

    activities = [
        {
            "time": "11:42 AM",
            "message": "Artwork uploaded for After Hours.",
        },
        {
            "time": "10:20 AM",
            "message": "Metadata updated for Blue Moon.",
        },
        {
            "time": "Yesterday",
            "message": "Marketing note added to Late Night Drive.",
        },
    ]

    return render_template(
        "dashboard.html",
        releases=releases,
        priorities=priorities,
        activities=activities,
    )