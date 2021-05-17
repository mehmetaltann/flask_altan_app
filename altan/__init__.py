from flask import Flask
from altan.extensions import db, login_manager, bootstrap
from altan.main import main
from altan.kisisel import kisisel
from altan.login import giris


def create_app(config_file='settings.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    app.register_blueprint(giris)
    app.register_blueprint(main)
    app.register_blueprint(kisisel)
    app.jinja_env.cache = {}
    return app
