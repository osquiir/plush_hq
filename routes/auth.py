
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
    login_user,
    logout_user,
)

from models.user import User


auth_bp = Blueprint(
    "auth",
    __name__,
)


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"],
)
def login():

    # If the user arrives at the login page,
    # close any previous session first.
    if request.method == "GET":

        if current_user.is_authenticated:
            logout_user()

        return render_template(
            "login.html"
        )


    # =====================================================
    # PROCESS LOGIN FORM
    # =====================================================

    email = request.form.get(
        "email",
        "",
    ).strip().lower()

    password = request.form.get(
        "password",
        "",
    )


    # Search user by email
    user = (
        User.query
        .filter_by(
            email=email
        )
        .first()
    )


    # =====================================================
    # VALIDATE CREDENTIALS
    # =====================================================

    if user is None or not user.check_password(password):

        flash(
            "Invalid email or password.",
            "danger",
        )

        return render_template(
            "login.html"
        )


    # =====================================================
    # CHECK ACCOUNT STATUS
    # =====================================================

    if not user.active:

        flash(
            "Your account has been deactivated. "
            "Please contact an administrator.",
            "danger",
        )

        return render_template(
            "login.html"
        )


    # =====================================================
    # LOGIN USER
    # =====================================================

    if not login_user(user):

        flash(
            "Unable to sign in. Please contact an administrator.",
            "danger",
        )

        return render_template(
            "login.html"
        )


    flash(
        f"Welcome back, {user.name}.",
        "success",
    )


    return redirect(
        url_for(
            "dashboard.dashboard"
        )
    )


# =========================================================
# LOGOUT
# =========================================================

@auth_bp.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been signed out.",
        "success",
    )

    return redirect(
        url_for(
            "auth.login"
        )
    )
