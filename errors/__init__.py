# coding=utf-8

from flask import Blueprint

# bp = Blueprint('errors', __name__, template_folder='templates')
bp = Blueprint('errors', __name__)

from volsteads.errors import handlers