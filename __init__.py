# # coding=utf-8
# import logging
# # from logging.handlers import SMTPHandler, RotatingFileHandler
# import os
# from flask import Flask, Request, current_app
# # from flask.ext.mongoalchemy import MongoAlchemy
# from flask_mongoalchemy import MongoAlchemy
# from flask_migrate import Migrate
# from flask_login import LoginManager
# from flask_mail import Mail
# from flask_bootstrap import Bootstrap
# # from flask_moment import Moment
# # from flask_babel import Babel, lazy_gettext as _1
# from config import Config
#
# # app = Flask(__name__)
# # app.config['MONGOALCHEMY_DATABASE'] = Config.DB_NAME
# # app.config['MONGOALCHEMY_SERVER'] = Config.DB_HOST
# # app.config['MONGOALCHEMY_PORT'] = Config.DB_PORT
# # app.config['MONGOALCHEMY_USER'] = Config.DB_USER
# # app.config['MONGOALCHEMY_PASSWORD'] = Config.DB_PW
# # app.config['MONGOALCHEMY_CONNECTION_STRING'] = 'mongodb://%s:%s@%s:%s/%s' % (Config.DB_USER, Config.DB_PW, Config.DB_HOST, Config.DB_PORT, Config.DB_NAME)
#
# db = MongoAlchemy()
# migrate = Migrate()
# login = LoginManager()
# # login.login_view = 'auth.login'
# # login.login_message = _1('Please log in to access this page')
# mail = Mail()
# bootstrap = Bootstrap()
# # moment = Moment()
# # babel = Babel()
#
# def create_app(config_class=Config):
#     app = Flask(__name__)
#     app.config.from_object(config_class)
#
#     db.init_app(app)
#     migrate.init_app(app, db)
#     login.init_app(app)
#     mail.init_app(app)
#     bootstrap.init_app(app)
# #     moment.init_app(app)
# #     babel.init_app(app)
#
#     from volsteads.errors import bp as errors_bp
#     app.register_blueprint(errors_bp)
#
#     from volsteads.auth import bp as auth_bp
#     app.register_blueprint(auth_bp, url_prefix='/auth')
#
#     from volsteads.main import bp as main_bp
#     app.register_blueprint(main_bp)
#
#     if not app.debug and not app.testing:
#         if app.config['MAIL_SERVER']:
#             auth = None
#             if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
#                 auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
#             secure = None
#             if app.config['MAIL_USE_TLS']:
#                 secure = ()
#
# from volsteads import routes, models