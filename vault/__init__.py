
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
from flask_user import UserManager

from vault.models import Employee

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _1('Authorized Users Must Log In To Access This Page')
mail = Mail()
bootstrap = Bootstrap()
babel = Babel()




user_first = ['Marley',
              'Jacob',
              'Ina',
              'Harrison',
              'Eleanor',
              'Heidi',
              'Rebecca',
              'Adam',
              'Jeff',
              'Cory',
              'Jennie',
              'Christopher',
              'Natalie']
user_last = ['Bartlett',
             'Boline',
             'Dale',
             'Easton',
             'Johnson',
             'Lundgren',
             'Mogck',
             'O\'Brien',
             'Petrovich',
             'Schuller',
             'Song',
             'Thompson',
             'Goodwin']
emp_id = [9, 2, 4, 12, 5, 7, 11, 10, 14, 3, 6, 8, 13]
user_pw = os.getenv('VOL_PW_LIST').split()
user_email = ['marleygirl22@gmail.com',
              'jkboline@gmail.com',
              'ina.dale55405@gmail.com',
              'harrisonbryc7@gmail.com',
              'egjohnson9@gmail.com',
              'lundgren.heidi@gmail.com',
              'rebeccamogck@gmail.com','padamlantz@gmail.com','jeff@volsteads.com','bar@volsteads.com','jjsong@gmail.com','cthompson369@outlook.com','natalie.erin.goodwin@gmail.com']
ringer_dict = {'Geoff':'Kemp', 'Joe':'Goff', 'Samantha':'Mulcahy', 'Brian':'Arnold', 'Stephen':'Engler', 'Korey':'Erikson','Matt':'Miotke','Marcelo':'Matos','Max':'Metakis'}




def create_users():

    user_list = []

    for i in range(len(user_email)):
        d = {'username':user_email[i],'email':user_email[i],'emp_id':emp_id[i],'first_name': user_first[i],'last_name':user_last[i], 'pw':user_pw[i]}
        user_list.append(d)
    from vault.models import User, Role, Employee
    for user_data in user_list:
        if not Employee.query.filter_by(first_name=user_data['first_name']).filter_by(last_name=user_data['last_name']).first():
            new_emp = Employee(first_name=user_data['first_name'], last_name=user_data['last_name'])
            db.session.add(new_emp)
    db.session.commit()

    for user_data in user_list:
        if not User.query.filter_by(email=user_data['email']).first():
            new_user_id = Employee.query.filter_by(first_name=user_data['first_name']).filter_by(last_name=user_data['last_name']).first().id
            new_user = User(username=user_data['email'], email=user_data['email'], emp_id=new_user_id)
            new_user.set_password(user_data['pw'])
            if user_data['email'] == "bar@volsteads.com" or user_data['email'] == "jeff@volsteads.com":
                admin_role = Role.query.filter_by(name='Admin').first()
                new_user.roles.append(admin_role)
            db.session.add(new_user)
        db.session.commit()


def create_sudo_employee():

    from vault.models import Employee, User, Role

    if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
        admin = Employee(first_name='admin', last_name='admin')
        db.session.add(admin)
        db.session.commit()
        return admin.id

def create_sudo_user(admin_id):
    from vault.models import Employee, User, Role
    if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() \
            and not User.query.filter(User.username == 'g1zmo').first():
        user = User(username='g1zmo', email='volsteads.vault@gmail.com',emp_id=admin_id)
        user.set_password(os.environ.get('VOL_ADMIN_PW'))
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Steward'))
        db.session.add(user)
        db.session.commit()


def create_ringers(name_dict: dict) -> bool:
    if name_dict and isinstance(name_dict, dict):
        for first in name_dict:
            new_emp = Employee(first_name=first,
                               last_name=name_dict[first],
                               ringer=True)
            db.session.add(new_emp)
        db.session.commit()
        return True
    else:
        return False

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.app_context().push()

    db.init_app(app)
    db.create_all()

    admin_id = create_sudo_employee()
    create_sudo_user(admin_id)
    create_users()
    create_ringers(ringer_dict)

    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)

    from vault.models import User, Role



    @app.context_processor
    def utility_processor():
        def get_roles():
            users = User.query.all();
            user_roles = {u.username:[role.name for role in u.roles] for u in users}
            target_user = current_user
            try:
                return user_roles[target_user.username]
            except AttributeError:
                return []
        return dict(get_roles=get_roles())


        # user_roles = {u.username:[role.name for role in u.roles] for u in users}
        # return user_roles


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

from vault import models

