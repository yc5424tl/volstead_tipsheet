# coding=utf-8
import os

from vault.models import User, Employee, Role
from datetime import datetime
# from vol_app import app
from flask import current_app


old_staff = ['Stephen Engler', 'Joe Goff', 'Samantha Mulcahy', 'Geoff Kemp', 'Brian Arnold']
support = ['Dane Cole', 'Korey Erickson', 'Matthew Miotke', 'Max Mateikis', 'Natalie Goodwin', 'Tyler O\'Brien' ]

user_first = [ 'Marley',
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
               'Natalie' ]

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

def populate_staff():
    print('begin populate_staff')
    for emp in emp_zip:
        if not Employee.query.filter_by(first_name=emp[0]).filter_by(last_name=emp[1]).first():
            em = Employee(first_name=emp[0], last_name=emp[1])
            em_id = em.id
            current_app.db.add(em)
        if not User.query.filter_by(username=em.first_name[0:3]+em.last_name).filter_by(email=emp[2]).filter_by(employee_id=em_id).first():
            new_user = User(username=em.first_name[0]+em.last_name, email=emp[2], employee_id=em_id)
            current_app.db.add(new_user)
            new_user.set_password(os.getenv('VOL_DEF_PW'))
            if new_user.username == 'cschuller' or new_user.username == 'jpetrovich':
                new_user.roles.append(Role(name='Admin'))
        current_app.db.commit()

    print('end populate_staff')
    return

# emp = (db.add(Employee(first_name=z[0], last_name=z[1], email=z[2])) for z in zip(user_first, user_last, email))




def create_sudo():
    if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
        admin = Employee(
            first_name='admin',
            last_name='admin')
        current_app.db.session.add(admin)
        current_app.db.session.commit()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() and not User.query.filter(User.username == 'g1zmo').first():
        admin_id = Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first().id
        user = User(
            username='g1zmo',
            email='volsteads.vault@gmail.com',
            email_confirmed_at=datetime.utcnow(),
            # password_hash=bcrypt.generate_password_hash(os.getenv('VOL_ADMIN_PW')),
            employee_id=admin_id
        )
        user.set_password(os.environ.get('VOL_ADMIN_PW'))
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Steward'))
        current_app.db.session.add(user)
        current_app.db.session.commit()
