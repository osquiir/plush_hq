from flask import Flask
from config import Config
from models import db
from routes.main import main_bp
from routes.dashboard import dashboard_bp
from routes.releases import releases_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(releases_bp)

    return app


app = create_app()


@app.route("/create-db")
def create_db():
    db.create_all()
    return "Database tables created successfully."


if __name__ == "__main__":
    app.run(debug=True)