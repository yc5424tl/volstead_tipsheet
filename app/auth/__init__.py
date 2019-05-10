# coding=utf-8

from flask import Blueprint
bp = Blueprint('auth', __name__)
from app.auth import routes
# from volsteads import LoginManager, models

# @LoginManager.user_loader
# def load_user(username):
#     target_user = volsteads.config['USERS_COLLECTION'].find_one({"_id": username})
#     if not target_user:
#         return None
#     return models.User(target_user['_id'])