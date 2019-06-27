
import logging
import os
from datetime import datetime
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, Blueprint

from flask_babel import Babel, lazy_gettext as _1
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, between

from config import Config
from vault.admin import CustomAdminView

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
    #db.create_all()

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

        from vault import models
        from vault.models import User, Employee, EmployeeReport, ShiftReport, Authorization, Role
        from vault.admin import Admin, AuthorizationView, EmployeeView, EmployeeReportView, RoleView, ShiftReportView, UserView
        from flask_admin.contrib.sqla import ModelView
        # admin_ctrl = Admin(app, name="Volstead's Vault", index_view=AdminView(ShiftReportView, db.session, url='/admin', endpoint='admin'))
        # admin.init_app(app=app)

        # admin_ctrl.add_view(AdminView(Authorization, db.session))
        # admin_ctrl.add_view(AdminView(Employee, db.session))
        # admin_ctrl.add_view(AdminView(EmployeeReport, db.session))
        # admin_ctrl.add_view(AdminView(Role, db.session))
        # admin_ctrl.add_view(AdminView(User, db.session))





        # admin_bp = Blueprint('admin', __name__, static_folder='static', template_folder='templates')

        # BELOW DID NOT WORK - MISSING SOME INTEGRATION BETWEEN ITSELF AND BLUEPRINTS IT SEEMS
        # admin.add_view(view=AuthorizationView)
        # admin.add_view(view=EmployeeView)
        # admin.add_view(view=EmployeeReportView)
        # admin.add_view(view=RoleView)
        # admin.add_view(view=ShiftReportView)
        # admin.add_view(view=UserView)

        # BELOW WORKED - how to customize?
        admin_ctrl = Admin(app, index_view=CustomAdminView())
        admin_ctrl.add_view(ModelView(Authorization, db.session))
        admin_ctrl.add_view(ModelView(Employee, db.session))
        admin_ctrl.add_view(ModelView(EmployeeReport, db.session))
        admin_ctrl.add_view(ModelView(Role, db.session))
        admin_ctrl.add_view(view=ModelView(name='Shift Reports', model=ShiftReport, session=db.session))
        admin_ctrl.add_view(view=ModelView(name='Users', model=User, session=db.session))

        # admin.add_view(ModelView(User, db.session))




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

        # from vault import models
        # from vault.models import User, Employee, EmployeeReport, ShiftReport, Authorization, Role

        @login.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        def earnings_for_year(emp: Employee, year: int):

            # shift_range_start = datetime.strptime(f'12/31/{str(year-1)}', '%m/%d/%Y')
            shift_range_start = datetime.strptime(f'6/20/{str(year)}', '%m/%d/%Y')
            shift_range_end = datetime.strptime(f'12/30/{str(year)}', '%m/%d/%Y')

            # EmployeeReport.query.filter_by(employee_id=emp.id).join(ShiftReport, and_(EmployeeReport.c.shift_id == shift.c.id, shift_range_start < ShiftReport.c.start_date < shift_range_end))

            # return EmployeeReport.query.join(ShiftReport, EmployeeReport.shift_id == ShiftReport.id).filter_by(employee_id=11)
            # return ShiftReport.query.join(EmployeeReport, EmployeeReport.shift_id == ShiftReport.id).filter_by(employee_id=11)
                # .filter_by( ShiftReport.start_date < shift_range_end).all()
                # .filter_by(EmployeeReport.id == emp.id).sum(EmployeeReport.cred_tips)
            # return EmployeeReport.query.filter_by(employee_id=emp.id).join(ShiftReport, EmployeeReport.shift_id==ShiftReport.id).filter_by(shift_range_start < ShiftReport.start_date < shift_range_end)
            return db.session.query(EmployeeReport).join(ShiftReport).\
                filter(EmployeeReport.employee_id==emp.id).filter(ShiftReport.start_date.between(shift_range_start, shift_range_end))

        emp = Employee.query.filter_by(last_name='BOLINE').first()
        print('emp -> ')
        print(emp)
        print('before earnings_for_year()')
        reports = earnings_for_year(emp, 2019)
        for report in reports:
            print(report)
        print('after earnings_for_year()')
        # admin = Admin.init_app(app)

        return app



