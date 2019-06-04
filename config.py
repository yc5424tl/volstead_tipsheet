import os
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('VOLSTEADS_SECRET_KEY') or 'eyes-of-the-night-king'
    SERVER_NAME = 'volsteads.vault:5000'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('VOL_SQL_DB') or 'sqlite:///' + os.path.join(basedir, 'volsteads_vault.db')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
    # CSRF_ENABLED = True

    SESSION_TYPE = 'filesystem'
    SESSION_COOKIE_DOMAIN = 'localhost.localdomain'
    SESSION_COOKIE_SECURE = False  # True will cause CSRF to fail.

    DB_URI = os.environ.get('PROD_MONGODB')
    DB_USER = urllib.parse.quote_plus(os.getenv('VOL_DB_USER'))
    DB_PW = urllib.parse.quote_plus(os.getenv('VOL_DB_PW'))
    DB_NAME = os.getenv('VOL_DB_NAME')
    DB_PORT = os.getenv('VOL_DB_PORT')
    DB_HOST = os.getenv('VOL_DB_PORT')

    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    USER_APP_NAME = os.environ.get('USER_APP_NAME')
    USER_ENABLE_EMAIL = os.environ.get('USER_ENABLE_EMAIL')
    USER_ENABLE_USERNAME = os.environ.get('USER_ENABLE_USERNAME')
    USER_EMAIL_SENDER_NAME = os.environ.get('USER_EMAIL_SENDER_NAME')
    USER_EMAIL_SENDER_EMAIL = os.environ.get('USER_EMAIL_SENDER_EMAIL')

    ADMINS = ['volsteads.vault@gmail.com']

    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
