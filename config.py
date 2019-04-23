import os


class Config(object):

    SECRET_KEY = os.environ.get('VOLSTEADS_SECRET_KEY') or 'eyes-of-the-night-king'
    DB_URI = os.environ.get('PROD_MONGODB')
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = None
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SERVER_NAME = 'localhost:5000'
    TEMPLATES_AUTO_RELOAD = True