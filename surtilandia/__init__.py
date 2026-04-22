from pathlib import Path

from flask import Flask

from .admin import admin_bp
from .config import get_base_config
from .db import close_db, init_app as init_db_app
from .store import store_bp


def create_app(test_config=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_mapping(get_base_config())

    if test_config:
        app.config.update(test_config)

    Path(app.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_DIR"]).mkdir(parents=True, exist_ok=True)

    init_db_app(app)
    app.teardown_appcontext(close_db)
    app.register_blueprint(admin_bp)
    app.register_blueprint(store_bp)

    return app
