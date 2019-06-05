# coding=utf-8
import os

from vault import create_app

app = create_app()
app.app_context().push()

from vault.models import User, ShiftReport, Employee, EmployeeReport, UserRoles, Role

def create_admin():

    from vault.models import User, Role, Employee
    from datetime import datetime

    # user_manager = UserManager(app_app, db, User)

    if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
        admin = Employee(first_name='admin',last_name='admin')
        app.db.session.add(admin)
        app.db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() and not User.query.filter(User.username=='g1zmo').first():
        admin_id = Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first().id
        user = User(username='g1zmo', email='volsteads.vault@gmail.com', email_confirmed_at=datetime.utcnow(), employee_id = admin_id)
        user.set_password(os.getenv('VOL_ADMIN_PW'))
        user.roles.append(Role(name='Admin'), Role(name='SysAdmin'))
        app.db.session.add(user)
        app.db.session.commit()

def populate_staff():
    from vault.models import User, Employee, Role

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

    email = ['marleygirl22@gmail.com',
             'jkboline@gmail.com',
             'ina.dale55408@gmail.com',
             'harrisonbryc7@gmail.com',
             'egjohnson9@gmail.com',
             'lundgren.heidi@gmail.com',
             'rebeccamogck@gmail.com',
             'padamlantz@gmail.com',
             'jeff@volsteads.com',
             'bar@volsteads.com',
             'jjsong@gmail.com',
             'cthompson369@outlook.com',
             'natalie.erin.goodwin@gmail.com']

    emp_zip = zip(user_first, user_last, email)

    print('begin populate_staff')

    for emp in emp_zip:

        if not Employee.query.filter_by(first_name=emp[0]).filter_by(last_name=emp[1]).first():
            em = Employee(first_name=emp[0], last_name=emp[1])
            em_id = em.id
            app.db.session.add(em)

        if not User.query.filter_by(username=em.first_name[0:3] + em.last_name).filter_by(email=emp[2]).filter_by(employee_id=em_id).first():
            new_user = User(username=em.first_name[0] + em.last_name, email=emp[2], employee_id=em_id)
            app.db.session.add(new_user)
            new_user.set_password(os.getenv('VOL_DEF_PW'))

            if new_user.username == 'cschuller' or new_user.username == 'jpetrovich':
                new_user.roles.append(Role(name='Admin'))

        app.db.session.commit()
    print('end populate_staff')

@app.shell_context_processor
def make_shell_context():
    return {'db': app.db,
            'User': User,
            'ShiftReport': ShiftReport,
            'Employee': Employee,
            'EmployeeReport': EmployeeReport,
            'Role': Role,
            'UserRoles': UserRoles}