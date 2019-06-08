import os
import urllib.parse

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('VOLSTEADS_SECRET_KEY') or 'eyes-of-the-night-king'
    if 'HEROKU_ENV' in os.environ:
        SERVER_NAME = 'volsteads.herokuapp.com'
        DEBUG = False
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        # SESSION_COOKIE_SECURE = True
        # REMEMBER_COOKIE_SECURE = True
        # REMEMBER_COOKIE_HTTPONLY = True
        # SESSION_COOKIE_HTTPONLY = True
    else:
        SERVER_NAME = 'volsteads.vault:5000'
        DEBUG = True
        SQLALCHEMY_DATABASE_URI = os.environ.get('VOL_DB_LOCAL')
        SESSION_TYPE = 'filesystem'
        SESSION_COOKIE_DOMAIN = 'localhost.localdomain'
        SESSION_COOKIE_SECURE = False  # True will cause CSRF to fail.

    # DATABASE_URI = os.environ.get('VOL_DB_LOCAL')

    # SQLALCHEMY_DATABASE_URI = os.environ.get('VOL_SQL_DB') or 'sqlite:///' + os.path.join(basedir, 'volsteads_vault.db')


    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'volsteads_vault.db')
    # DATABASE_URI ="""postgres://nvzcupoeotolbv:0c882d6c37b4e1815393a65db73b28a004e022af2856c4ade68930eab1207ab2@ec2-50-19-109-120.compute-1.amazonaws.com:5432/d223t0ngtli997"""
    #
    # SQLALCHEMY_DATABASE_URI = """postgres://nvzcupoeotolbv:0c882d6c37b4e1815393a65db73b28a004e022af2856c4ade68930eab1207ab2@ec2-50-19-109-120.compute-1.amazonaws.com:5432/d223t0ngtli997"""

    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_CHECK_DEFAULT = False
    WTF_CSRF_ENABLED = False
    CSRF_ENABLED = False
    # CSRF_ENABLED = True


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
