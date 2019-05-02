# coding=utf-8

from flask import Blueprint

bp = Blueprint('errors', __name__, template_folder='templates')

from volsteads.errors import handlers