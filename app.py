from dotenv import load_dotenv

load_dotenv()

from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import db
from models.user import User

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.releases import releases_bp
from routes.users import users_bp
from routes.artists import artists_bp
from routes.calendar import calendar_bp

from zoneinfo import ZoneInfo
from datetime import timezone

app = Flask(__name__)
app.config.from_object(Config)

# =========================================================
# TIMEZONE
# =========================================================

PACIFIC_TIME = ZoneInfo(
    "America/Los_Angeles"
)


@app.template_filter(
    "pacific_time"
)
def pacific_time(value):

    if value is None:
        return ""

    # Existing timestamps in Plush are stored as UTC
    # but may be timezone-naive.
    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    local_time = value.astimezone(
        PACIFIC_TIME
    )

    return local_time.strftime(
        "%b %d, %Y at %I:%M %p"
    )

db.init_app(app)


# =========================================================
# FLASK-LOGIN
# =========================================================

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth.login"
login_manager.login_message = "Please sign in to access the platform."
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(
        User,
        int(user_id),
    )


# =========================================================
# LANDING
# =========================================================

@app.route("/")
def landing():
    return render_template(
        "landing.html"
    )


# =========================================================
# BLUEPRINTS
# =========================================================

app.register_blueprint(
    dashboard_bp
)

app.register_blueprint(
    releases_bp
)

app.register_blueprint(
    auth_bp
)

app.register_blueprint(
    users_bp
)

app.register_blueprint(
    artists_bp
)

app.register_blueprint(
    calendar_bp
)
# =========================================================
# LOCAL DEVELOPMENT
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True
    )