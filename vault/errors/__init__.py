# coding=utf-8

from flask import Blueprint
bp = Blueprint('errors', __name__)
from vault.errors import handlers