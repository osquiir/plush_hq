from functools import wraps

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

from models import db
from models.artist import Artist
from models.user import User


users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users",
)


# =========================================================
# ADMIN ONLY DECORATOR
# =========================================================

def admin_required(view_function):

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if not current_user.is_authenticated:
            return redirect(
                url_for("auth.login")
            )

        if not current_user.is_admin():

            flash(
                "You do not have permission to access this page.",
                "danger",
            )

            return redirect(
                url_for("dashboard.dashboard")
            )

        return view_function(
            *args,
            **kwargs,
        )

    return wrapped_view


# =========================================================
# USER LIST
# =========================================================

@users_bp.route("/")
@login_required
@admin_required
def users():

    all_users = (
        User.query
        .order_by(User.name.asc())
        .all()
    )

    return render_template(
        "users.html",
        users=all_users,
    )


# =========================================================
# CREATE USER
# =========================================================

@users_bp.route(
    "/new",
    methods=["GET", "POST"],
)
@login_required
@admin_required
def create_user():

    artists = (
        Artist.query
        .order_by(Artist.name.asc())
        .all()
    )

    if request.method == "POST":

        name = request.form.get(
            "name",
            "",
        ).strip()

        email = request.form.get(
            "email",
            "",
        ).strip().lower()

        password = request.form.get(
            "password",
            "",
        )

        role = request.form.get(
            "role",
            "team",
        ).strip().lower()

        artist_mode = request.form.get(
            "artist_mode",
            "existing",
        ).strip().lower()

        existing_artist_id = request.form.get(
            "artist_id",
            "",
        ).strip()

        new_artist_name = request.form.get(
            "new_artist_name",
            "",
        ).strip()

        new_artist_email = request.form.get(
            "new_artist_email",
            "",
        ).strip()

        new_artist_genre = request.form.get(
            "new_artist_genre",
            "",
        ).strip()


        allowed_roles = {
            "admin",
            "team",
            "artist",
        }


        if not name or not email or not password:

            flash(
                "Name, email and password are required.",
                "danger",
            )

            return render_template(
                "new_user.html",
                artists=artists,
            )


        if role not in allowed_roles:
            role = "team"


        existing_user = (
            User.query
            .filter_by(email=email)
            .first()
        )


        if existing_user:

            flash(
                "A user with this email already exists.",
                "danger",
            )

            return render_template(
                "new_user.html",
                artists=artists,
            )


        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "danger",
            )

            return render_template(
                "new_user.html",
                artists=artists,
            )


        artist_id = None


        # =================================================
        # ARTIST ACCOUNT
        # =================================================

        if role == "artist":

            if artist_mode == "existing":

                if not existing_artist_id:

                    flash(
                        "Please select an existing artist.",
                        "danger",
                    )

                    return render_template(
                        "new_user.html",
                        artists=artists,
                    )

                try:
                    artist_id = int(
                        existing_artist_id
                    )

                except ValueError:

                    flash(
                        "The selected artist is invalid.",
                        "danger",
                    )

                    return render_template(
                        "new_user.html",
                        artists=artists,
                    )


                artist = db.session.get(
                    Artist,
                    artist_id,
                )


                if artist is None:

                    flash(
                        "The selected artist does not exist.",
                        "danger",
                    )

                    return render_template(
                        "new_user.html",
                        artists=artists,
                    )


            elif artist_mode == "new":

                if not new_artist_name:

                    flash(
                        "Artist name is required.",
                        "danger",
                    )

                    return render_template(
                        "new_user.html",
                        artists=artists,
                    )


                existing_artist = (
                    Artist.query
                    .filter(
                        db.func.lower(
                            Artist.name
                        )
                        == new_artist_name.lower()
                    )
                    .first()
                )


                if existing_artist:

                    flash(
                        "An artist with this name already exists. "
                        "Please select the existing artist instead.",
                        "danger",
                    )

                    return render_template(
                        "new_user.html",
                        artists=artists,
                    )


                artist = Artist(
                    name=new_artist_name,
                    email=(
                        new_artist_email
                        or email
                    ),
                    genre=(
                        new_artist_genre
                        or None
                    ),
                )

                db.session.add(
                    artist
                )

                db.session.flush()

                artist_id = artist.id


            else:

                flash(
                    "Invalid artist selection mode.",
                    "danger",
                )

                return render_template(
                    "new_user.html",
                    artists=artists,
                )


        # =================================================
        # CREATE USER
        # =================================================

        user = User(
            name=name,
            email=email,
            role=role,
            artist_id=artist_id,
        )

        user.set_password(
            password
        )

        db.session.add(
            user
        )

        db.session.commit()


        flash(
            "User created successfully.",
            "success",
        )


        return redirect(
            url_for("users.users")
        )


    return render_template(
        "new_user.html",
        artists=artists,
    )