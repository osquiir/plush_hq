import calendar
from datetime import date

from flask import (
    Blueprint,
    abort,
    render_template,
    request,
)

from flask_login import (
    current_user,
    login_required,
)

from models.release import Release


calendar_bp = Blueprint(
    "calendar",
    __name__,
    url_prefix="/calendar",
)


# =========================================================
# CALENDAR
# =========================================================

@calendar_bp.route("/")
@login_required
def calendar_view():

    # Artists cannot access the calendar.
    if current_user.is_artist():
        abort(403)


    today = date.today()


    # -----------------------------------------------------
    # MONTH / YEAR
    # -----------------------------------------------------

    try:

        year = int(
            request.args.get(
                "year",
                today.year,
            )
        )

        month = int(
            request.args.get(
                "month",
                today.month,
            )
        )

    except ValueError:

        year = today.year
        month = today.month


    if month < 1 or month > 12:

        year = today.year
        month = today.month


    # -----------------------------------------------------
    # RELEASES
    # -----------------------------------------------------

    releases = (
        Release.query
        .filter(
            Release.release_date.isnot(None)
        )
        .order_by(
            Release.release_date.asc()
        )
        .all()
    )


    releases_by_day = {}


    for release in releases:

        if (
            release.release_date.year == year
            and release.release_date.month == month
        ):

            day = release.release_date.day

            releases_by_day.setdefault(
                day,
                [],
            ).append(
                release
            )


    # -----------------------------------------------------
    # CALENDAR MATRIX
    # -----------------------------------------------------

    month_calendar = calendar.Calendar(
        firstweekday=6
    ).monthdayscalendar(
        year,
        month,
    )


    month_name = calendar.month_name[
        month
    ]


    # -----------------------------------------------------
    # PREVIOUS MONTH
    # -----------------------------------------------------

    if month == 1:

        previous_month = 12
        previous_year = year - 1

    else:

        previous_month = month - 1
        previous_year = year


    # -----------------------------------------------------
    # NEXT MONTH
    # -----------------------------------------------------

    if month == 12:

        next_month = 1
        next_year = year + 1

    else:

        next_month = month + 1
        next_year = year


    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_name=month_name,
        month_calendar=month_calendar,
        releases_by_day=releases_by_day,
        today=today,
        previous_month=previous_month,
        previous_year=previous_year,
        next_month=next_month,
        next_year=next_year,
    )