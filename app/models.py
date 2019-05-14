# coding=utf-8

from datetime import datetime
from hashlib import md5
from logging import Logger
from time import time

from sqlalchemy import CheckConstraint
import jwt
from flask import current_app
from flask_user import UserManager, UserMixin
# from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login
from app.main import shift as shift_data




class User(db.Model, UserMixin):
    __tablename__ = 'user_table'

    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    email = db.Column(db.String(128, collation='NOCASE'), index=True, unique=True, nullable=False)
    last_online = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), index=True, unique=True, nullable=False)
    employee = db.relationship('Employee', foreign_keys='User.employee_id', backref='user_emp', lazy=True , uselist=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_model.id'), nullable=False)
    roles = db.relationship('Role', secondary='user_role_table', backref=db.backref('user_table', lazy='dynamic'))


    # def __init__(self, email, password_hash, username, employee_id):
    #     self._email = email
    #     self._password_hash = password_hash
    #     self._username = username
    #     self._employee_id = employee_id

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return -1
        return User.query.get(user_id)




class Role(db.Model):
    __tablename__ = 'role_table'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    # def __init__(self, name):
    #     self._name = name




class UserRoles(db.Model):
    __tablename__ = 'user_roles_table'

    id = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey('role_table.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user_table.id', ondelete='CASCADE'))

    # def __init__(self, role_id, user_id):
    #     self._role_id = role_id
    #     self._user_id = user_id




class EmployeeReport(db.Model):
    __tablename__ = 'employee_report_table'

    id = db.Column(db.Integer, primary_key=True)
    cash_tips = db.Column(db.Float)
    cc_tips = db.Column(db.Float)
    role = db.Column(db.Enum('SERVICE', 'SUPPORT', name='role'), nullable=False)
    shift_hours = db.Column(db.Float)
    tip_hours = db.Column(db.Float)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee_table.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift_report_table.id'), nullable=False)

    __table_args__ = (
        CheckConstraint(10000 > cash_tips, name='check_cash_tips_max'),
        CheckConstraint(0 < cash_tips, name='check_cash_tips_min'),
        CheckConstraint(10000 > cc_tips, name='check_cc_tips_max'),
        CheckConstraint(0 < cc_tips, name='check_cc_tips_min'),
        CheckConstraint(24.0 > shift_hours, name="check_shift_hours_max"),
        CheckConstraint(0 < shift_hours, name="check_shift_hours_min"),
        CheckConstraint(24.0 > tip_hours, name='check_tip_hours_max'),
        CheckConstraint(0 < tip_hours, name="check_tip_hours_min"))


    def __repr__(self):
        return '<Employee Report {} {}>'.format(self.shift.start_date, self.employee.full_name)
    # def __init__(self, cash_tips, cc_tips, role, shift_hours, tip_hours, shift_id):
    #     self._cash_tips = cash_tips
    #     self._cc_tips = cc_tips
    #     self._role = role
    #     self._shift_hours = shift_hours
    #     self._tip_hours = tip_hours
    #     self._shift_id = shift_id




class ShiftReport(db.Model):
    __tablename__ = 'shift_report_table'

    id = db.Column(db.Integer, primary_key=True)
    cash_subtotals = db.Column(db.PickleType)
    cash_tip_pool = db.Column(db.Float)
    cash_tip_wage = db.Column(db.Float)
    cc_tip_pool = db.Column(db.Float)
    cc_tip_wage = db.Column(db.Float)
    start_date = db.Column(db.DateTime, index=True, unique=True)
    total_shift_hours = db.Column(db.Float)
    total_tip_hours = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    staff_report =  db.Column(db.PickleType(db.PickleType))
    employee_report = db.relationship('EmployeeReport', backref='shift_report', lazy=True)

    __table_args__ = (
        CheckConstraint(10000 > cash_tip_pool, name='check_cash_tip_pool_max'),
        CheckConstraint(0 < cash_tip_pool, name='check_cash_tip_pool_min'),
        CheckConstraint(100 > cash_tip_wage, name='check_cash_tip_wage_max'),
        CheckConstraint(0 < cash_tip_wage, name='check_cash_tip_wage_min'),
        CheckConstraint(24 > total_shift_hours, name='check_total_shift_hours_max'),
        CheckConstraint(0 < total_shift_hours, name='check_total_shift_hours_min'),
        CheckConstraint(24 > total_tip_hours, name='check_total_tip_hours_max'),
        CheckConstraint(0 < total_tip_hours, name='check_total_tip_hours_min'),
        CheckConstraint(10000 > cc_tip_pool, name='check_cc_tip_pool_max'),
        CheckConstraint(0 < cc_tip_pool, name='check_cc_tip_pool_min'),
        CheckConstraint(100 > cc_tip_wage, name='check_cc_tip_wage_max'),
        CheckConstraint(0 < cc_tip_wage, name='check_cc_tip_wage_min'))

    # def __init__(self, shift_report: Shift ):
    #     self.cash_subtotals = shift_report.cash_subtotals
    #     self.cash_tip_pool = shift_report.cash_tip_pool
    #     self.cash_tip_wage = shift_report.cash_tip_wage
    #     self.cc_tip_pool = shift_report.cc_tip_pool
    #     self.cc_tip_wage = shift_report.cc_tip_wage
    #     self.start_date = shift_report.start_date
    #     self.total_shift_hours = shift_report.shift_hours
    #     self.total_tip_hours = shift_report.tip_hours
    #     self.staff_report = shift_report.staff_report

    def __repr__(self):
        return '<Shift Report {}'.format(self.start_date)

    def build_shift_report(self):
        self.get_cash_tip_pool()

    def get_cash_tip_pool(self, shift: shift_data):
        tip_pool = 0.0
        for denom in shift.cash_subtotals:
            tip_pool += shift.cash_subtotals[denom]
        self.cash_tip_pool = tip_pool

    @staticmethod
    def insert_new_shift(shift: shift_data) -> bool:
        new_shift = ShiftReport(shift.start_date, shift.total_shift_hours, shift.total_tip_hour,
                                shift.cc_tip_pool, shift.cc_tip_wage, shift.cash_tip_pool,
                                shift.cash_tip_wage, shift.cash_subtotals, shift.staff_report,
                                shift.created_at)
        try:
            db.session.add(new_shift)
            db.session.commit()
            return True
        except Exception:
            print('Error adding new shift to db.')
            return False




class Employee(db.Model):
    __tablename__ = 'employee_table'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    user = db.relationship('User', foreign_keys='Employee.user_id', backref='emp_user', lazy=True, uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user_table.id'), nullable=False)
    employee_reports = db.relationship('EmployeeReport', backref='rep_user', lazy=True)

    # def __init__(self, first_name, last_name, user_id):
    #     self._first_name = first_name
    #     self._last_name = last_name
    #     self._user_id = user_id

    def __repr__(self):
        return '<Employee {}>'.format(self.full_name)

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name



@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


user_manager = UserManager(current_app, db, User)
# db.create_all()
#
# if not User.query.filter(User.email == 'member@example.com').first():
#     user = User(email='member@example.com',password=user_manager.hash_password('Password1'),)
#     db.session.add(user)
#     db.session.commit()
#
# if not User.query.filter(User.email == 'admin@example.com').first():
#     user = User(email='admin@example.com', password=user_manager.hash_password('Password1'),)
#     user.roles.append(Role(name='Admin'))
#     user.roles.append(Role(name='Agent'))
#     db.session.add(user)
#     db.session.commit()

# class HashField:
#     def set_value(self, instance, value, from_db=False):
#         if from_db:
#             super(HashField, self).set_value(instance, value)
#         else:
#             super(HashField, self).set_value(instance, str(hash(value)))




def add_new_emp(self, emp: {Employee}):
    try:
        self._db.employee.update({'first_name': emp.first_name,
                                  'last_name': emp.last_name,
                                  'shift_hours': emp.shift_hours,
                                  'tip_hours': emp.tip_hours,
                                  'tip_role': emp.role,
                                  'tip_total': emp.tip_total})
    except :
        Logger.log(msg='Operation to add new employee did not complete.')

#
# def create_emp_index() -> bool:
#     try:
#         db.employee.create_index([('last_name', db.ASCENDING), ('first_name', db.ASCENDING)], unique=True, name='Employee Index')
#         return True
#     except KeyError:
#         return False
#
# def build_shift_report(shift: Shift) -> dict:
#     shift.get_cash_tip_pool()
#     shift_report = {
#         'start_date': shift.start_date,
#         'total_shift_hours': float(shift.shift_hours),
#         'total_tip_hours': float(shift.tip_hours),
#         'cc_tip_pool': float(shift.cc_tip_pool),
#         'cc_tip_wage': float(shift.cc_tip_wage),
#         'cash_tip_pool': float(shift.cash_tip_pool),
#         'cash_tip_wage': float(shift.cash_tip_wage),
#         'cash_subtotals': shift.cash_subtotals,
#         'staff_report': None
#     }
#     return shift_report
#
#
# def submit_daily_report(daily_report: dict) -> bool:
#         db.test_daily_report.update_one({}, {"$set": daily_report}, upsert=True)
#         return True
