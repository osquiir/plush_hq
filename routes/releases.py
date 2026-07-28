from flask import Blueprint, render_template

releases_bp = Blueprint("releases", __name__)


@releases_bp.route("/releases")
def releases():
    return "<h1>Releases coming soon</h1>"


@releases_bp.route("/releases/<int:release_id>")
def release_detail(release_id):
    release = {
        "id": release_id,
        "artist": "Mia Rose",
        "title": "After Hours",
        "type": "Single",
        "status": "Needs Attention",
        "release_date": "Aug 02, 2026",
        "stage": "Artwork Approval",
        "budget": "5,000",
        "progress": 60,
    }

    tasks = [
        {"name": "Deal signed", "completed": True},
        {"name": "Producer agreement signed", "completed": True},
        {"name": "Marketing ideation", "completed": True},
        {"name": "Team intro/meeting", "completed": True},
        {"name": "Master delivered", "completed": True},
        {"name": "Song metadata completed", "completed": False},
        {"name": "Artwork created/approved", "completed": False},
        {"name": "Spotify canvas approved", "completed": False},
        {"name": "Marketing budget agreed upon", "completed": False},
        {"name": "Rollout plan developed", "completed": False},
        {"name": "Song ingestion", "completed": False},
        {"name": "Playlist pitching", "completed": False},
        {"name": "Release date", "completed": False},
    ]

    files = [
        {"name": "master_v2.wav", "category": "Audio"},
        {"name": "lyrics.docx", "category": "Lyrics"},
        {"name": "cover_artwork.png", "category": "Artwork"},
        {"name": "producer_agreement.pdf", "category": "Contract"},
    ]

    notes = [
        {
            "content": "Artwork needs final approval before Friday.",
            "visibility": "Internal",
        },
        {
            "content": "Artist requested a darker visual direction.",
            "visibility": "Artist Visible",
        },
    ]

    ai_summary = (
        "This release is 60% complete. The main blocker is artwork approval. "
        "Metadata and Spotify Canvas are still pending."
    )

    return render_template(
        "release_detail.html",
        release=release,
        tasks=tasks,
        files=files,
        notes=notes,
        ai_summary=ai_summary,
    )