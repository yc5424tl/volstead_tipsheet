
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

# user_first_list = os.environ.get('VOL_EMP_LIST_1')###
# user_last_list = os.environ.get('VOL_EMP_LIST_2')   ####
# emp_id_list = os.environ.get('VOL_EMP_ID_LIST') ###
# user_pw_list = os.environ.get('VOL_PW_LIST').split()###
# user_email_list = os.environ.get('VOL_USER_EMAIL_LIST')###
# ringer_dict = os.environ.get('VOL_RINGER_DICT')
#
# def create_users():
#
#     from vault import models
#
#     user_list = []
#     starter = models.Role.query.filter_by(name='STARTER').first()
#     manager = models.Role.query.filter_by(name='MANAGER').first()
#
#     for i in range(len(user_email_list)):
#         n = i - 1
#         d = {'username':user_email_list[n],'email':user_email_list[n],'emp_id':emp_id_list[n],
#              'first_name': user_first_list[n],'last_name':user_last_list[n], 'pw':user_pw_list[n]}
#         if user_first_list[n] == 'Jeff' and user_last_list[n] == 'Petrovich':
#             d['roles'] = manager
#         else:
#             d['roles'] = starter
#         user_list.append(d)
#
#     for ringer in ringer_dict:
#         r = {''}
#
#     emp_to_commit = False
#
#     for user_data in user_list:
#         if not models.Employee.query.filter_by(first_name=user_data['first_name']).filter_by(last_name=user_data['last_name']).first():
#             new_emp = models.Employee(first_name=user_data['first_name'], last_name=user_data['last_name'])
#             db.session.add(new_emp)
#             print('setting emp_to_commit to True')
#             emp_to_commit = True
#
#     print('checking emp_to_commit before commiting session')
#     print('emp_to_commit = ' + str(emp_to_commit))
#     if emp_to_commit:
#         db.session.commit()
#
#     user_to_commit = False
#     for user_data in user_list:
#         if not models.User.query.filter_by(email=user_data['email']).first():
#             new_user_id = models.Employee.query.filter_by(first_name=user_data['first_name']).filter_by(last_name=user_data['last_name']).first().id
#             new_user = models.User(username=user_data['email'], email=user_data['email'], emp_id=new_user_id)
#             new_user.set_password(user_data['pw'])
#             if user_data['email'] == "bar@volsteads.com" or user_data['email'] == "jeff@volsteads.com":
#                 admin_auth = models.Authorization.query.filter_by(name='Admin').first()
#                 new_user.Authorizations.append(admin_auth)
#             db.session.add(new_user)
#             user_to_commit = True
#     if user_to_commit:
#         db.session.commit()
#
#
# def create_sudo_employee():
#
#     from .models import Employee, User, Role
#
#     if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
#         admin = Employee(first_name='admin', last_name='admin')
#         db.session.add(admin)
#         db.session.commit()
#         return admin.id
#
# def create_sudo_user(admin_id):
#     from vault.models import Employee, User, Authorization
#     if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() \
#             and not User.query.filter(User.username == 'g1zmo').first():
#         user = User(username='g1zmo', email='volsteads.vault@gmail.com',emp_id=admin_id)
#         user.set_password(os.environ.get('VOL_ADMIN_PW'))
#         user.authorizations.append(Authorization(name='Admin'))
#         user.authorizations.append(Authorization(name='Steward'))
#         db.session.add(user)
#         db.session.commit()


# def create_ringers(name_dict: dict) -> bool:
#     from vault.models import Employee
#     if name_dict and isinstance(name_dict, dict):
#         for first in name_dict:
#             new_emp = Employee(first_name=first,
#                                last_name=name_dict[first],
#                                ringer=True)
#             db.session.add(new_emp)
#         db.session.commit()
#         return True
#     else:
#         return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    # admin_id = create_sudo_employee()
    # create_sudo_user(admin_id)
    # create_users()
    # create_ringers(ringer_dict)

    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)



    @app.context_processor
    def utility_processor():
        def get_authorizations():
            users = User.query.all()
            user_auths = {u.username:[authorization.name for authorization in u.authorizations] for u in users}
            target_user = current_user
            try:
                return user_auths[target_user.username]
            except AttributeError:
                return []
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



