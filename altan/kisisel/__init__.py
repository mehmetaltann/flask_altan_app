from flask import Blueprint

kisisel = Blueprint("kisisel", __name__)

from altan.kisisel import routes
