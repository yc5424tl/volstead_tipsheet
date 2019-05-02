# import enum
#
# from manage import db
#
# class Employee(db.Model):
#
#     __tablename__ = 'employees'
#
#     emp_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     emp_name = db.Column(db.String, nullable=False)
#     emp_role = db.Column(db.Enum(EmpRoleEnum), nullable=False)
#
#
# class Shift(db.Model):
#
#     __tablename__ = 'shifts'
#
#     shift_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     shift_hours = db.Column(db.Integer,)
#     emp_id = db.relationship('Employees', backref='shifts', cascade='all, delete-orphan', lazy='dynamic')
#
#
# class EmpRoleEnum(enum.Enum):
#     service = 1.00
#     support = 0.65

from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
#TODO from volsteads import db, login

# class Employee(UserMixin, db.Model)