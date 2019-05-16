import os
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):

    SECRET_KEY = os.environ.get('VOLSTEADS_SECRET_KEY') \
                 or 'eyes-of-the-night-king'
    SQLALCHEMY_DATABASE_URI = os.environ.get('VOL_SQL_DB') or 'sqlite:///' + os.path.join(basedir, 'volsteads_vault.db')
    SERVER_NAME = 'localhost:5000'
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = 'sqlalchemy'

    DB_URI = os.environ.get('PROD_MONGODB')
    DB_USER = urllib.parse.quote_plus(os.getenv('VOL_DB_USER'))
    DB_PW = urllib.parse.quote_plus(os.getenv('VOL_DB_PW'))
    DB_NAME = os.getenv('VOL_DB_NAME')
    DB_PORT = os.getenv('VOL_DB_PORT')
    DB_HOST = os.getenv('VOL_DB_PORT')

    MONGO_URI = 'mongodb://%s:%s@%s:%s/%s' % (DB_USER, DB_PW, DB_HOST, DB_PORT, DB_NAME)

    # MONGOALCHEMY_CONNECTION_STRING = 'mongodb://%s:%s@%s:%s/%s' % (DB_USER, DB_PW, DB_HOST, DB_PORT, DB_NAME)

    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = None
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    # SERVER_NAME = 'localhost:5000'
    TEMPLATES_AUTO_RELOAD = True


    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['jkboline@gmail.com']

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')

    USER_APP_NAME = 'VolsteadsVault'

