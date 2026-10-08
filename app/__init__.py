import os

from flask import Flask

from . import db, routes


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        DATABASE=os.environ.get("SPENDLY_DB", "spendly.db"),
        CURRENCY=os.environ.get("SPENDLY_CURRENCY", "$"),
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-change-me"),
    )
    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    app.register_blueprint(routes.bp)
    return app
