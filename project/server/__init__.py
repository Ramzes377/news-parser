import os

from flask import Flask
from flask_migrate import Migrate

from project.server.models import db


def create_app():
    app = Flask(
        __name__,
        template_folder="../client/templates",
        static_folder="../client/static",
    )
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)
    app.config['SERVER_NAME'] = '127.0.0.1:5000'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI", 'postgresql://postgres:admin@host.docker.internal:5432/news-parser')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    migrate = Migrate()
    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate.init_app(app, db)

    from project.server.views import main_blueprint
    app.register_blueprint(main_blueprint)
    app.shell_context_processor({"app": app})
    main_blueprint.app_context = app.app_context()
    return app
