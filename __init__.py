
import logging
from flask_pymongo import PyMongo, MongoClient
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, Request, current_app
# from flask.ext.mongoalchemy import MongoAlchemy
# from flask_mongoalchemy import MongoAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel, lazy_gettext as _1
# from flask_moment import Moment
# from flask_babel import Babel, lazy_gettext as _1
from config import Config

from db_mgr import DbController as db

from volsteads import routes, models, errors
#
# # app = Flask(__name__)
# # app.config['MONGOALCHEMY_DATABASE'] = Config.DB_NAME
# # app.config['MONGOALCHEMY_SERVER'] = Config.DB_HOST
# # app.config['MONGOALCHEMY_PORT'] = Config.DB_PORT
# # app.config['MONGOALCHEMY_USER'] = Config.DB_USER
# # app.config['MONGOALCHEMY_PASSWORD'] = Config.DB_PW
# # app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://%s:%s@%s:%s/%s' % (Config.DB_USER, Config.DB_PW, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME)
#
# db = MongoAlchemy()x
mongo = PyMongo()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
login.login_message = _1('Please log in to access this page.')
# login.login_view = 'auth.login'
# login.login_message = _1('Please log in to access this page')
mail = Mail()
bootstrap = Bootstrap()
babel = Babel()
# moment = Moment()
# babel = Babel()'



def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    if db.connect_db():
        print('Connected to DB')
    else:
        'DB connection failed'
    # mongo_connection = MongoClient(Config.DB_HOST,)
#
#
    mongo.init_app(app)
    migrate.init_app(app, mongo)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)
#     moment.init_app(app)
#     babel.init_app(app)





    from volsteads.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from volsteads.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from volsteads.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddr=app.config['ADMINS'], subject="Volstead's Vault Vexed",
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/volsteads.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Volstead's Vault startup")

    return app



# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(current_app.config['LANGUAGES'])
#
# # from volsteads import routes, models