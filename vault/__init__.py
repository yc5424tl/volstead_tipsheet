
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from flask_babel import Babel, lazy_gettext as _1
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _1('Authorized Users Must Log In To Access This Page')

mail = Mail()
bootstrap = Bootstrap()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)

    @app.context_processor
    def utility_processor():
        def get_authorizations():
            users = User.query.all()
            user_auth = {u.username:u.authorization.name for u in users}
            target_user = current_user
            try:
                return user_auth[target_user.username]
            except AttributeError:
                return 'READ_ONLY'
        return dict(get_authorizations = get_authorizations())

    if __name__ != '__main__':
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    with app.app_context():

        from vault.errors import bp as errors_bp
        app.register_blueprint(errors_bp)

        from vault.auth import bp as auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')

        from vault.main import bp as main_bp
        app.register_blueprint(main_bp)

        if not app.debug and not app.testing:

            if app.config['MAIL_SERVER']:
                auth = None

                if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                    auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                secure = None

                if app.config['MAIL_USE_TLS'] is True:
                    secure = True

                mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                    toaddrs=app.config['ADMINS'][0],
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
                file_handler = RotatingFileHandler('logs/volsteads.log', maxBytes=10240, backupCount=10)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s '
                    '[in %(pathname)s:%(lineno)d]'))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info("Volstead's Vault startup")

        from vault import models
        from vault.models import User, Employee

        @login.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        return app



