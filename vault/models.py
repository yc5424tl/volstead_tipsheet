# coding=utf-8
from datetime import datetime
from hashlib import md5
from time import time

import bcrypt
import jwt
import os
import argon2
from flask import current_app, logging
# from flask_bcrypt import generate_password_hash, check_password_hash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import CheckConstraint, create_engine, Index
from sqlalchemy.orm import backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from vault import db, login
from vault.main.employee_data_controller import EmployeeDataController
from vault.main.shift_data_controller import ShiftDataController

Base = declarative_base()
ROUNDS = 5
hasher = argon2.PasswordHasher()
##################################################################################################################################
##    USER
##################################################################################################################################

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    # Refactor models subclassing declarative base, which will allow the use of psql ilike and therefore multi-column uniqueness (i.e. first and last name) as a secondary index
    id = db.Column(db.Integer(), primary_key=True)
    username           = db.Column(db.String(128), nullable=False, unique=True)
    active             = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    password_hash      = db.Column(db.String(255), nullable=False)
    email              = db.Column(db.String(255), nullable=False, unique=True, index=True)
    email_confirmed_at = db.Column(db.DateTime())
    last_online        = db.Column(db.DateTime(), default=datetime.utcnow)
    employee_id        = db.Column(db.Integer(), db.ForeignKey('employee.id'))
    employee           = db.relationship('Employee', backref=backref('user_by_employee', uselist=False), primaryjoin="Employee.id == User.employee_id")
    roles              = db.relationship('Role', secondary='user_roles')

    def __init__(self, username, email, emp_id, active=True):
        self.username = username
        self.email = email
        self.active = active
        self.employee_id = emp_id
        self.email_confirmed_at = datetime.utcnow()

    def set_password(self, password):
        self.password_hash = hasher.hash(password)

    def check_password(self, password):
        try:
            hasher.verify(self.password_hash, password)
            if hasher.check_needs_rehash(self.password_hash):
                self.set_password(password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False
        except argon2.exceptions.VerificationError:
            return False
        except argon2.exceptions.InvalidHash:
            return False



    # def set_password(self, password):
    #     self.password_hash = bcrypt.hashpw(password.encode('utf-8'), None)
    #     # self.password_hash = generate_password_hash(password)
    #
    # def check_password(self, password):
    #     # return check_password_hash(self.password_hash, password)
    #     # return bcrypt.checkpw(password.encode('utf-8'), self.password_hash)
    #     return self.password_hash == bcrypt.hashpw(password.encode('utf-8')).decode()
    #     # return bcrypt.checkpw(password, self.password_hash)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in}, current_app.config['SECRET_KEY'], algorithm='HS256')\
            .decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return -1
        return User.query.get(user_id)


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# @login.user_loader
# def load_user(user_id):
#     try:
#         # u = User.query.get(user_id)
#         # return User(id=u.id,
#         #         username=u.username,
#         #         password_hash=u.password_hash,
#         #         email=u.email,
#         #         email_confirmed_at=u.email_confirmed_at,
#         #         employee_id=u.employee_id)
#         return User.get(User.id==user_id)
#     except User.DoesNotExist:
#         return None




################################################################################################################################
##    SHIFT REPORT
##################################################################################################################################

class ShiftReport(db.Model):

    __tablename__ = 'shift_reports'

    id               = db.Column(db.Integer(), primary_key=True)
    cash_tip_pool    = db.Column(db.Float())
    cash_tip_wage    = db.Column(db.Float())
    cred_tip_pool    = db.Column(db.Float())
    cred_tip_wage    = db.Column(db.Float())
    shift_hours      = db.Column(db.Float())
    tip_hours        = db.Column(db.Float())
    start_date       = db.Column(db.DateTime(), index=True, unique=True)
    created_at       = db.Column(db.DateTime(), default=datetime.utcnow)


    __table_args__ = (
        CheckConstraint(10000 > cash_tip_pool, name='check_cash_tip_pool_max'),
        CheckConstraint(0     < cash_tip_pool, name='check_cash_tip_pool_min'),
        CheckConstraint(100   > cash_tip_wage, name='check_cash_tip_wage_max'),
        CheckConstraint(0     < cash_tip_wage, name='check_cash_tip_wage_min'),
        CheckConstraint(90    > shift_hours,   name='check_total_shift_hours_max'), # full staff +1 all 5-cl
        CheckConstraint(0     < shift_hours,   name='check_total_shift_hours_min'),
        CheckConstraint(90    > tip_hours,     name='check_total_tip_hours_max'),
        CheckConstraint(0     < tip_hours,     name='check_total_tip_hours_min'),
        CheckConstraint(10000 > cred_tip_pool, name='check_cc_tip_pool_max'),
        CheckConstraint(0     < cred_tip_pool, name='check_cc_tip_pool_min'),
        CheckConstraint(100   > cred_tip_wage, name='check_cc_tip_wage_max'),
        CheckConstraint(0     < cred_tip_wage, name='check_cc_tip_wage_min'))

    def __repr__(self):
        return '<Shift Report {}>'.format(self.start_date)

    @staticmethod
    def populate_fields(shift: ShiftDataController):
        return ShiftReport(
            cash_tip_pool = shift.cash_tip_pool,
            cash_tip_wage = shift.cash_tip_wage,
            cred_tip_pool = shift.cred_tip_pool,
            cred_tip_wage = shift.cred_tip_wage,
            shift_hours   = shift.shift_hours,
            tip_hours     = shift.tip_hours,
            start_date    = shift.start_date,
        )


# class Employee(Base):
#     __tablename__ = 'employee'
#     __table_args__ = (
#         Index(
#             'unique_full_name',
#             'first_name', 'last_name',
#             unique=True
#         ),
#     )
#     id = db.Column(db.Integer, db.Sequence('id_seq'), primary_key=True)
#     first_name = db.Column(db.String(64))
#     last_name = db.Column(db.String(64))
#     created_at = db.Column(db.DateTime(), default=datetime.utcnow)
#
#     def __init__(self, first_name, last_name):
#         self.first_name = first_name
#         self.last_name = last_name
#
#     def __repr__(self):
#         return '<Employee {} {}>'.format(
#             self.first_name,
#             self.last_name
#         )
#
#     @property
#     def full_name(self):
#         return '%s %s'.format(self.first_name, self.last_name)
#
#     @full_name.setter
#     def full_name(self, new_name):
#         self.full_name = new_name



##################################################################################################################################
##    EMPLOYEE
##################################################################################################################################



class Employee(db.Model):

    __tablename__ = 'employee'

    id              = db.Column(db.Integer(), primary_key=True)
    first_name      = db.Column(db.String(64))
    last_name       = db.Column(db.String(64))
    created_at      = db.Column(db.DateTime(), default=datetime.utcnow)

    # __table_args__ = (
    #     db.UniqueConstraint('first_name', 'last_name', name='first_last_uni_emp'),
    # )

    def __repr__(self):
        return '<Employee {} {}>'.format(
            self.first_name,
            self.last_name
        )

    @property
    def full_name(self):
        return '%s %s'.format(self.first_name, self.last_name)

    @full_name.setter
    def full_name(self, new_name):
        self.full_name = new_name




###################################################################################################################################
##    EMPLOYEE REPORT
##################################################################################################################################

class EmployeeReport(db.Model):

    __tablename__ = 'employee_report'

    id          = db.Column(db.Integer(), primary_key=True)
    cash_tips   = db.Column(db.Float())
    cred_tips   = db.Column(db.Float())
    tip_role    = db.Column(db.Enum('SERVICE', 'SUPPORT', name="tip_role"))
    shift_hours = db.Column(db.Float())
    tip_hours   = db.Column(db.Float())
    employee_id = db.Column(db.Integer(), db.ForeignKey('employee.id'))
    employee    = db.relationship('Employee', backref=db.backref('employee_reports', lazy='joined'), primaryjoin="EmployeeReport.employee_id == Employee.id")
    shift_id    = db.Column(db.Integer(), db.ForeignKey('shift_reports.id'))
    shift       = db.relationship('ShiftReport', backref=db.backref('employee_reports', lazy='joined'), primaryjoin="EmployeeReport.shift_id == ShiftReport.id")


    __table_args__ = (
        CheckConstraint(10000 > cash_tips,   name='check_cash_tips_max'),
        CheckConstraint(0     < cash_tips,   name='check_cash_tips_min'),
        CheckConstraint(10000 > cred_tips,   name='check_cc_tips_max'),
        CheckConstraint(0     < cred_tips,   name='check_cc_tips_min'),
        CheckConstraint(24.0  > shift_hours, name="check_shift_hours_max"),
        CheckConstraint(0     < shift_hours, name="check_shift_hours_min"),
        CheckConstraint(24.0  > tip_hours,   name='check_tip_hours_max'),
        CheckConstraint(0     < tip_hours,   name="check_tip_hours_min"))

    def __repr__(self):
        return '<Employee Report {} {}>'.format(
            self.shift.start_date,
            self.employee.full_name
        )

    @staticmethod
    def populate_fields(employee_report: EmployeeDataController, shift_id, employee_id):
        return EmployeeReport(
        cash_tips   = employee_report.cash_tips,
        cred_tips   = employee_report.cred_tips,
        tip_role    = employee_report.tip_role,
        shift_hours = employee_report.shift_hours,
        tip_hours   = employee_report.tip_hours,
        shift_id    = shift_id,
        employee_id = employee_id
        )




###################################################################################################################################
##    ROLE
##################################################################################################################################

class Role(db.Model):

    __tablename__ = 'roles'

    id   = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.name)




###################################################################################################################################
##    USER ROLES
###################################################################################################################################

class UserRoles(db.Model):

    __tablename__ = 'user_roles'

    id      = db.Column(db.Integer(), primary_key=True)
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))


# user_manager = flask_user.UserManager(current_app, db, User)
# engine = create_engine(os.environ.get('VOL_DB_LOCAL'))
# Session = sessionmaker(bind=engine)
# session = Session()
# # Base.metadata.create_all(engine, Base.metadata.tables["employee"])
# Base.metadata.create_all(engine, tables=[Employee.__table__])
