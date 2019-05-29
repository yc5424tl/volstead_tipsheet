# coding=utf-8
import os

from app.models import User, Employee, Role
from datetime import datetime
from app import db, bcrypt

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
         'Christopher']

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
             'Thompson']

email = ['marleygirl22@gmail.com',
         'jkboline@gmail.com',
         'ina.dale55408@gmail.com',
         'harrisonbryc7@gmail.com',
         'egjohnson9@gmail.com',
         'heidi@example.com',
         'rebecca@example.com',
         'adam@example.com',
         'jp@example.com',
         'schuller@example.com',
         'jjsong@gmail.com',
         'cthompson369@outlook.com']

emp_zip = zip(user_first, user_last, email)
for emp in emp_zip:
    em = Employee(first_name=emp[0], last_name=emp[1])
    em_id = em.id
    db.add(em)
    user = User(username=em.first_name[0:3]+em.last_name, email=emp[2], employee_id=em_id)
    db.add(user)
    user.set_password(os.getenv('VOL_DEF_PW'))
db.commit()

# emp = (db.add(Employee(first_name=z[0], last_name=z[1], email=z[2])) for z in zip(user_first, user_last, email))


old_staff = ['Stephen Engler', 'Joe Goff', 'Samantha Mulcahy', 'Geoff Kemp', 'Brian Arnold']
support = ['Dane Cole', 'Korey Erickson', 'Matthew Miotke', 'Max Mateikis', 'Natalie Goodwin', 'Tyler O\'Brien' ]


if not Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first():
    admin = Employee(
        first_name='admin',
        last_name='admin')
    db.session.add(admin)
    db.session.commit()

# Create 'admin@example.com' user with 'Admin' and 'Agent' roles
if not User.query.filter(User.email == 'volsteads.vault@gmail.com').first() and not User.query.filter(User.username == 'g1zmo').first():
    admin_id = Employee.query.filter_by(first_name='admin').filter_by(last_name='admin').first().id
    user = User(
        username='g1zmo',
        email='volsteads.vault@gmail.com',
        email_confirmed_at=datetime.utcnow(),
        password_hash=bcrypt.generate_password_hash(os.getenv('VOL_ADMIN_PW')),
        employee_id=admin_id
    )
    user.roles.append(Role(name='Admin'))
    user.roles.append(Role(name='Agent'))
    db.session.add(user)
    db.session.commit()
