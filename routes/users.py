from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from models import db
from models.user import User


users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/users",
)


@users_bp.route("/")
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


@users_bp.route("/new", methods=["GET", "POST"])
def create_user():

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
                "new_user.html"
            )


        if role not in allowed_roles:
            role = "team"


        existing_user = User.query.filter_by(
            email=email
        ).first()


        if existing_user:

            flash(
                "A user with this email already exists.",
                "danger",
            )

            return render_template(
                "new_user.html"
            )


        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "danger",
            )

            return render_template(
                "new_user.html"
            )


        user = User(
            name=name,
            email=email,
            role=role,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()


        flash(
            "User created successfully.",
            "success",
        )


        return redirect(
            url_for("users.users")
        )


    return render_template(
        "new_user.html"
    )