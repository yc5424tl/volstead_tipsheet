import os


class Config(object):

    SECRET_KEY = os.environ.get('VOLSTEADS_SECRET_KEY') or 'eyes-of-the-night-king'
    DB_URI = os.environ.get('PROD_MONGODB')

    DB_USER = os.getenv('VOL_DB_USER')

    DB_PW = os.getenv('VOL_DB_PW')

    DB_NAME = os.getenv('VOL_DB_NAME')

    DB_PORT = os.getenv('VOL_DB_PORT')

    DB_HOST = os.getenv('VOL_DB_PORT')

    MONGOALCHEMY_CONNECTION_STRING = 'mongodb://%s:%s@%s:%s/%s' % (DB_USER, DB_PW, DB_HOST, DB_PORT, DB_NAME)

    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = None
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SERVER_NAME = 'localhost:5000'
    TEMPLATES_AUTO_RELOAD = True