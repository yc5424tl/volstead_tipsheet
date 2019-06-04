
from flask import Blueprint
bp = Blueprint('main', __name__)
from vault.main import routes