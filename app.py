from flask import Flask, render_template
from flask_login import LoginManager

from config import Config
from models import db
from models.user import User

from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.releases import releases_bp
from routes.users import users_bp


app = Flask(__name__)
app.config.from_object(Config)

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
# DEVELOPMENT DATABASE ROUTE
# =========================================================

@app.route("/create-db")
def create_db():
    db.create_all()

    return "Database tables created successfully."


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


# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True
    )