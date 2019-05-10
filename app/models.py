
from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from app import db, login
from app.main import employee as emp_data, shift as shift_data


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    employee = db.relationship('Employee', backref='user', lazy='dynamic')
    last_online = db.Column(db.Datetime, default=datetime.utcnow)

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
            return
        return User.query.get(user_id)

@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date, index=True, unique=True)
    total_shift_hours = db.Column(db.Float, min=0.5)
    total_tip_hours = db.Column(db.Float, min=0.5)
    cc_tip_pool = db.Column(db.Float, min=0)
    cc_tip_wage = db.Column(db.Float, min=0)
    cash_tip_pool = db.Column(db.Float, min=0)
    cash_tip_wage = db.Column(db.Float, min=0)
    cash_subtotals = db.Column(db.PickleType)
    staff_report =  db.Column(db.Array(db.PickleType))

    def build_shift_report(self):
        self.get_cash_tip_pool()


    def get_cash_tip_pool(self, shift: shift_data):
        tip_pool = 0.0
        for denom in shift.cash_subtotals:
            tip_pool += shift.cash_subtotals[denom]
        self.cash_tip_pool = tip_pool


# import base64
# import os
# from logging import Logger
#
# import pymongo
# import pytz
# from pymongo.errors import DuplicateKeyError
# from config import Config
# from datetime import datetime, timedelta
# import calendar
# from hashlib import md5
# from time import time
# from flask import current_app
# from flask_login import UserMixin
# # from flask_jwt import JWT, jwt_required, current_identity
# from google.auth import jwt
# from werkzeug.security import generate_password_hash, check_password_hash, safe_str_cmp
# from app import login, db
#
#
#
# class HashField():
#     def set_value(self, instance, value, from_db=False):
#         if from_db:
#             super(HashField, self).set_value(instance, value)
#         else:
#             super(HashField, self).set_value(instance, str(hash(value)))
#
#
# class User(UserMixin):
#     id = db.StringField()
#     username = db.StringFIeld(max_length=30, min_length=5)
#     email = db.StringField(max_length=50, min_length=6)
#     password_hash = db.HashField()
#     token = db.StringField()
#     token_expiration = db.DateTimeField()
#     employee_id = db.StringField()
#
#
#
#     def __init__(self, username):
#         self._username = username
#
#
#
#     def __repr__(self):
#         return '<User {}>'.format(self.username)
#
# # Below are implemented by the Flask-Login mixin UserMixin
# #     def is_authenticated(self):
# #         return True
# #
# #     def is_active(self):
# #         return True
# #
# #     def is_anonymous(self):
# #         return False
# #
# #     def get_id(self):
# #         return self._username
#
#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)
#
#
#
#     @staticmethod
#     def check_password(password_hash, password):
#         return check_password_hash(password_hash, password)
#
#
#
#     def avatar(self, size):
#         digest = md5(self.email.lower().encode('utf-8')).hexdigest()
#         return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
#
#
#
#     def from_dict(self, data, new_user=False):
#         for field in ['username', 'email', 'about_me']:
#             if field in data:
#                 setattr(self, field, data[field])
#             if new_user and 'password' in data:
#                 self.set_password(data['password'])
#
#
#
#     # def get_reset_password_token(self):
#     #     exp_time = datetime.now() + timedelta(minutes=10)
#     #     return jwt.encode(
#     #         {'reset_password': self.id, 'exp': exp_time}, key_id= current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
#
#     def get_reset_password_token(self, expires_in=600):
#         return jwt.encode(
#             {'reset_password': self.id, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256').decode('utf-8')
#
#     @staticmethod
#     def verify_reset_password_token(token):
#         try:
#             user_id = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['reset_password']
#
#         except:
#             return
#         return db.users(user_id)
#
#
#
#     # @staticmethod
#     # def verify_reset_password_token(token):
#     #     try:
#     #         user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
#     #     except:
#     #         return User.query.get(user_id)
#         # return jwt.encode(
#         #     {'reset_password': self.id, 'exp': (datetime.utcnow() + datetime.timedelta(seconds=expires_in)}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
#         # expires = datetime.utcnow() + timedelta(minutes=10)
#         # jwt_payload = jwt.encode({'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(minutes=10)}, key_id=current_app.config['SECRET_KEY'], algorithm='RS256').decode('utf-8')
#         # return jwt.encode({'reset_password': self.id, 'exp': calendar.calender.timegm(expires.timetuple())}, current_app.config.SECRET_KEY, algorithm='HS256')
#
#     # @staticmethod
#     # def verify_reset_password_token(token):
#     #     try:
#     #         # user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
#     #     user_id = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])['reset_password']
#     #     except UnicodeDecodeError:
#     #         return
#     #     return User.query.get(user_id)
#
#     def get_token(self, expires_in=3600):
#         now = datetime.utcnow()
#         if self.token and self.token_expiration > now + timedelta(minutes=660):
#             return self.token
#         self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
#         self.token_expiration = now + timedelta(seconds=expires_in)
#         db.session.add(self)
#         return self.token
#
#
#     def revoke_token(self):
#         self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
#
#
#
#     @staticmethod
#     def check_token(token):
#         user = User.query.filter_by(token=token).first()
#         if user is None or user.token_expiration < datetime.utcnow():
#             return None
#         return user
#
#
#
#
# @login.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
#
#
#
# class Employee(db.Document):
#     first_name = db.StringField(max_length=45, min_length=1)
#     last_name = db.StringField(max_length=45, min_length=1)
#     role = db.EnumField(db.StringField('SERVICE', 'SUPPORT'))
#     shift_hours = db.FloatField(max_value=9, min_value = 0)
#     tip_hours = db.FloatField(max_value = 9, min_value = 0)
#     cash_tips = db.FloatField(max_value=5000, min_value=0)
#     cc_tips = db.FloatField(max_value=5000, min_value=0)
#
#     def full_name(self) -> str:
#         name = self.first_name + ' ' + self.last_name
#         return name
#
#
#
# class Shift(db.Document):
#     staff = db.ListField(Employee)
#     cc_tip_pool = db.FloatField(max_value=50000, min_value=0)
#     cash_subtotals = db.DictField(value_type=db.FloatField)
#     shift_hours = db.FloatField(max_value=100, min_value=0)
#     tip_hours = db.FloatField(max_value=100, min_value=0)
#     cash_tip_wage = db.FloatField(max_value=100, min_value=0)
#     cc_tip_wage = db.FloatField(max_value=100, min_value=0)
#     start_date = db.DateTimeField(min_date=datetime(2018,12,31,0,0,0), use_tz=pytz.timezone('US/Central'))
#     cash_tip_pool = db.FloatField(max_value=50000, min_value=0)
#
#
# def build_staff_report(staff: [Employee]) -> []:
#     staff_report = {}
#     for emp in staff:
#         emp_report = {'first_name': emp.first_name,
#                       'last_name': emp.last_name,
#                       'shift_hours': float(emp.shift_hours),
#                       'tip_hours': float(emp.tip_hours),
#                       'tip_role': emp.role,
#                       'cc_tips': float(emp.cc_tips),
#                       'cash_tips': float(emp.cash_tips),
#                       'shift_summary': emp.shift_details}
#         new_data = {emp.full_name: emp_report}
#         staff_report.update(new_data)
#     return staff_report
#
# def add_new_emp(self, emp: {Employee}):
#     try:
#         self._db.employee.update({'first_name': emp.first_name,
#                                   'last_name': emp.last_name,
#                                   'shift_hours': emp.shift_hours,
#                                   'tip_hours': emp.tip_hours,
#                                   'tip_role': emp.role,
#                                   'tip_total': emp.tip_total})
#     except DuplicateKeyError:
#         Logger.log(msg='Operation to add new employee encountered a duplicate key.')
#
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
