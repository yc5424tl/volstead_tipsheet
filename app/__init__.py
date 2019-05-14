
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, Request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
# from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _1
from config import Config



db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _1('Authorized Users Must Log In To Access This Page')
mail = Mail()
bootstrap = Bootstrap()
# moment.init_app(app)
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()
    # with app.app_context():
    #     db.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    # moment.init_app(app)
    babel.init_app(app)


    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:

        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'],
                        app.config['MAIL_PASSWORD'])
            secure = None

            if app.config['MAIL_USE_TLS']:
                secure = ()

            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddr=app.config['ADMINS'],
                subject="Volstead's Vault Vexed",
                credentials=auth,
                secure=secure)

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

# db.drop_all()
# db.create_all()
from app import models
# from volsteads.app.models import UserManager, UserModel, RoleModel
#
# user_manager = UserManager(current_app, db, UserModel)
#
#
# if not UserModel.query.filter(UserModel.email == 'member@example.com').first():
#     user = UserModel(Modelemail='member@example.com', password=user_manager.hash_password('Password1'), )
#     db.session.add(user)
#     db.session.commit()
#
# if not UserModel.query.filter(UserModel.email == 'admin@example.com').first():
#     user = UserModel(email='admin@example.com', password=user_manager.hash_password('Password1'), )
#     user.roles.append(RoleModel(name='Admin'))
#     user.roles.append(RoleModel(name='Agent'))
#     db.session.add(user)
#     db.session.commit()
    # from app import models



# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(current_app.config['LANGUAGES'])
#
# # from volsteads import routes, models