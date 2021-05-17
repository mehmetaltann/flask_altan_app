from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
from flask_bootstrap import Bootstrap

db = SQLAlchemy()
login_manager = LoginManager()
bootstrap = Bootstrap()
