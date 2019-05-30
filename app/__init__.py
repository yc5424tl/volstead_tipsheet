
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask


# from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel, lazy_gettext as _1
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _1('Authorized Users Must Log In To Access This Page')
mail = Mail()
bootstrap = Bootstrap()
# bcrypt = Bcrypt()
babel = Babel()


def create_admin(app_db, app_app):

    from app.models import User, Role, Employee
    from datetime import datetime

    # user_manager = UserManager(app_app, db, User)

    if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
        admin = Employee(
            first_name='admin',
            last_name='admin'
        )
        db.session.add(admin)
        db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() and not User.query.filter(User.username=='g1zmo').first():
        admin_id = Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first().id
        user = User(
            username='g1zmo',
            email='volsteads.vault@gmail.com',
            email_confirmed_at=datetime.utcnow(),
            # password_hash=bcrypt.generate_password_hash(os.getenv('VOL_ADMIN_PW')),
            employee_id = admin_id
        )
        user.set_password(os.getenv('VOL_ADMIN_PW'))
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        app_db.session.add(user)
        app_db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    create_admin(db, app)

    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    # bcrypt.init_app(app)
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
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
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
            file_handler = RotatingFileHandler('logs/volsteads.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Volstead's Vault startup")

    from app import models
    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

# from app import models
