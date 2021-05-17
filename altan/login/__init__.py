from flask import Blueprint

giris = Blueprint("giris", __name__)

from altan.login import routes