import os
from datetime import date
from uuid import uuid4

from dotenv import load_dotenv

from flask import (
    Blueprint,
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

from supabase import create_client
from werkzeug.utils import secure_filename

from models import db
from models.artist import Artist


# =========================================================
# ENVIRONMENT / SUPABASE
# =========================================================

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


artists_bp = Blueprint(
    "artists",
    __name__,
    url_prefix="/artists",
)


# =========================================================
# IMAGE SETTINGS
# =========================================================

ALLOWED_IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# =========================================================
# HELPERS
# =========================================================

def get_artist_image_signed_url(
    storage_path,
):

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
            "Artist image signed URL error:",
            error,
        )

        return None


def upload_artist_image(
    artist,
    uploaded_file,
):

    if (
        uploaded_file is None
        or uploaded_file.filename == ""
    ):
        return None


    original_filename = secure_filename(
        uploaded_file.filename
    )


    if not original_filename:

        raise ValueError(
            "Invalid image filename."
        )


    extension = (
        os.path.splitext(
            original_filename
        )[1]
        .lower()
    )


    if extension not in ALLOWED_IMAGE_EXTENSIONS:

        raise ValueError(
            "Artist image must be JPG, JPEG, PNG, or WEBP."
        )


    stored_filename = (
        f"{uuid4().hex}"
        f"{extension}"
    )


    storage_path = (
        f"artists/"
        f"{artist.id}/"
        f"{stored_filename}"
    )


    file_bytes = (
        uploaded_file.read()
    )


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


    return storage_path


def delete_artist_image(
    storage_path,
):

    if not storage_path:
        return

    try:

        (
            supabase
            .storage
            .from_(SUPABASE_BUCKET)
            .remove(
                [storage_path]
            )
        )

    except Exception as error:

        print(
            "Artist image delete error:",
            error,
        )


def prepare_artist_image(
    artist,
):

    artist.display_image_url = (
        get_artist_image_signed_url(
            artist.image_url
        )
    )

    return artist


# =========================================================
# LIST ARTISTS
# =========================================================

@artists_bp.route("/")
@login_required
def artists():

    if current_user.is_artist():

        if current_user.artist_id is None:

            all_artists = []

        else:

            artist = db.session.get(
                Artist,
                current_user.artist_id,
            )

            all_artists = (
                [artist]
                if artist
                else []
            )

    else:

        all_artists = (
            Artist.query
            .order_by(
                Artist.name.asc()
            )
            .all()
        )


    for artist in all_artists:

        prepare_artist_image(
            artist
        )


    return render_template(
        "artists.html",
        artists=all_artists,
    )


# =========================================================
# ARTIST DETAIL
# =========================================================

@artists_bp.route(
    "/<int:artist_id>"
)
@login_required
def artist_detail(
    artist_id,
):

    artist = (
        Artist.query.get_or_404(
            artist_id
        )
    )


    if (
        current_user.is_artist()
        and current_user.artist_id
        != artist.id
    ):

        flash(
            "You do not have permission to access this artist.",
            "danger",
        )

        return redirect(
            url_for(
                "artists.artists"
            )
        )


    prepare_artist_image(
        artist
    )


    releases = sorted(
        artist.releases,
        key=lambda release: (
            release.release_date
            or date.max
        ),
    )


    return render_template(
        "artist_detail.html",
        artist=artist,
        releases=releases,
    )


# =========================================================
# CREATE ARTIST
# =========================================================

@artists_bp.route(
    "/new",
    methods=["GET", "POST"],
)
@login_required
def create_artist():

    if current_user.is_artist():

        flash(
            "Artist accounts have view-only access.",
            "danger",
        )

        return redirect(
            url_for(
                "artists.artists"
            )
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()

        genre = request.form.get(
            "genre",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip()

        instagram_url = request.form.get(
            "instagram_url",
            "",
        ).strip()

        spotify_url = request.form.get(
            "spotify_url",
            "",
        ).strip()

        tiktok_url = request.form.get(
            "tiktok_url",
            "",
        ).strip()

        youtube_url = request.form.get(
            "youtube_url",
            "",
        ).strip()


        uploaded_image = (
            request.files.get(
                "artist_image"
            )
        )


        if not name:

            flash(
                "Artist name is required.",
                "danger",
            )

            return render_template(
                "new_artist.html"
            )


        existing_artist = (
            Artist.query
            .filter(
                db.func.lower(
                    Artist.name
                )
                == name.lower()
            )
            .first()
        )


        if existing_artist:

            flash(
                "An artist with this name already exists.",
                "danger",
            )

            return render_template(
                "new_artist.html"
            )


        artist = Artist(
            name=name,
            genre=genre or None,
            email=email or None,
            instagram_url=(
                instagram_url
                or None
            ),
            spotify_url=(
                spotify_url
                or None
            ),
            tiktok_url=(
                tiktok_url
                or None
            ),
            youtube_url=(
                youtube_url
                or None
            ),
            image_url=None,
        )


        try:

            db.session.add(
                artist
            )

            # We need the artist ID
            # before creating the Storage path.
            db.session.flush()


            if (
                uploaded_image
                and uploaded_image.filename
            ):

                artist.image_url = (
                    upload_artist_image(
                        artist,
                        uploaded_image,
                    )
                )


            db.session.commit()


        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

            return render_template(
                "new_artist.html"
            )


        except Exception as error:

            db.session.rollback()

            print(
                "Create artist error:",
                error,
            )

            flash(
                "The artist could not be created.",
                "danger",
            )

            return render_template(
                "new_artist.html"
            )


        flash(
            "Artist created successfully.",
            "success",
        )


        return redirect(
            url_for(
                "artists.artist_detail",
                artist_id=artist.id,
            )
        )


    return render_template(
        "new_artist.html"
    )


# =========================================================
# EDIT ARTIST
# =========================================================

@artists_bp.route(
    "/<int:artist_id>/edit",
    methods=["GET", "POST"],
)
@login_required
def edit_artist(
    artist_id,
):

    artist = (
        Artist.query.get_or_404(
            artist_id
        )
    )


    if current_user.is_artist():

        flash(
            "Artist accounts have view-only access.",
            "danger",
        )

        return redirect(
            url_for(
                "artists.artist_detail",
                artist_id=artist.id,
            )
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()


        if not name:

            flash(
                "Artist name is required.",
                "danger",
            )

            prepare_artist_image(
                artist
            )

            return render_template(
                "edit_artist.html",
                artist=artist,
            )


        artist.name = name


        artist.genre = (
            request.form.get(
                "genre",
                "",
            ).strip()
            or None
        )


        artist.email = (
            request.form.get(
                "email",
                "",
            ).strip()
            or None
        )


        artist.instagram_url = (
            request.form.get(
                "instagram_url",
                "",
            ).strip()
            or None
        )


        artist.spotify_url = (
            request.form.get(
                "spotify_url",
                "",
            ).strip()
            or None
        )


        artist.tiktok_url = (
            request.form.get(
                "tiktok_url",
                "",
            ).strip()
            or None
        )


        artist.youtube_url = (
            request.form.get(
                "youtube_url",
                "",
            ).strip()
            or None
        )


        uploaded_image = (
            request.files.get(
                "artist_image"
            )
        )


        old_image_path = (
            artist.image_url
        )


        try:

            if (
                uploaded_image
                and uploaded_image.filename
            ):

                new_image_path = (
                    upload_artist_image(
                        artist,
                        uploaded_image,
                    )
                )

                artist.image_url = (
                    new_image_path
                )


            db.session.commit()


            # Delete old image only after
            # the new data was saved.
            if (
                uploaded_image
                and uploaded_image.filename
                and old_image_path
                and old_image_path
                != artist.image_url
            ):

                delete_artist_image(
                    old_image_path
                )


        except ValueError as error:

            db.session.rollback()

            flash(
                str(error),
                "danger",
            )

            prepare_artist_image(
                artist
            )

            return render_template(
                "edit_artist.html",
                artist=artist,
            )


        except Exception as error:

            db.session.rollback()

            print(
                "Edit artist error:",
                error,
            )

            flash(
                "The artist could not be updated.",
                "danger",
            )

            prepare_artist_image(
                artist
            )

            return render_template(
                "edit_artist.html",
                artist=artist,
            )


        flash(
            "Artist updated successfully.",
            "success",
        )


        return redirect(
            url_for(
                "artists.artist_detail",
                artist_id=artist.id,
            )
        )


    prepare_artist_image(
        artist
    )


    return render_template(
        "edit_artist.html",
        artist=artist,
    )