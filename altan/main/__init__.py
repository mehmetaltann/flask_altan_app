from flask import Blueprint

main = Blueprint("main", __name__)

from altan.main import routes
