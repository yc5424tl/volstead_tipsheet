

from flask import Blueprint

bp = Blueprint('main', __name__)

from volsteads.main import routes