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
import base64
import os
import pytz
from config import Config
from datetime import datetime, timedelta
import calendar
from hashlib import md5
from time import time
from flask import current_app
from flask_login import UserMixin
# from flask_jwt import JWT, jwt_required, current_identity
from google.auth import jwt
from werkzeug.security import generate_password_hash, check_password_hash, safe_str_cmp
from volsteads import mongo, login

#TODO from volsteads import db, login


class HashField(mongo.db.StringField):
    def set_value(self, instance, value, from_db=False):
        if from_db:
            super(HashField, self).set_value(instance, value)
        else:
            super(HashField, self).set_value(instance, str(hash(value)))


class User(UserMixin, mongo.db.Document):
    id = mongo.db.StringField()
    username = mongo.db.StringFIeld(max_length=30, min_length=5)
    email = mongo.db.StringField(max_length=50, min_length=6)
    password_hash = mongo.db.HashField()
    token = mongo.db.StringField()
    token_expiration = mongo.db.DateTimeField()
    employee_id = mongo.db.StringField()



    def __init__(self, username):
        self._username = username



    def __repr__(self):
        return '<User {}>'.format(self.username)

# Below are implemented by the Flask-Login mixin UserMixin
#     def is_authenticated(self):
#         return True
#
#     def is_active(self):
#         return True
#
#     def is_anonymous(self):
#         return False
#
#     def get_id(self):
#         return self._username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)



    @staticmethod
    def check_password(password_hash, password):
        return check_password_hash(password_hash, password)



    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)



    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
            if new_user and 'password' in data:
                self.set_password(data['password'])



    # def get_reset_password_token(self):
    #     exp_time = datetime.now() + timedelta(minutes=10)
    #     return jwt.encode(
    #         {'reset_password': self.id, 'exp': exp_time}, key_id= current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            user_id = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])['reset_password']

        except:
            return
        return User.query.get(user_id)



    # @staticmethod
    # def verify_reset_password_token(token):
    #     try:
    #         user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    #     except:
    #         return User.query.get(user_id)
        # return jwt.encode(
        #     {'reset_password': self.id, 'exp': (datetime.utcnow() + datetime.timedelta(seconds=expires_in)}, current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
        # expires = datetime.utcnow() + timedelta(minutes=10)
        # jwt_payload = jwt.encode({'reset_password': self.id, 'exp': datetime.utcnow() + timedelta(minutes=10)}, key_id=current_app.config['SECRET_KEY'], algorithm='RS256').decode('utf-8')
        # return jwt.encode({'reset_password': self.id, 'exp': calendar.calender.timegm(expires.timetuple())}, current_app.config.SECRET_KEY, algorithm='HS256')

    # @staticmethod
    # def verify_reset_password_token(token):
    #     try:
    #         # user_id = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
    #     user_id = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])['reset_password']
    #     except UnicodeDecodeError:
    #         return
    #     return User.query.get(user_id)

    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(minutes=660):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        mongo.db.session.add(self)
        return self.token


    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)



    @staticmethod
    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user




@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class Employee(mongo.db.Document):
    first_name = mongo.db.StringField(max_length=45, min_length=1)
    last_name = mongo.db.StringField(max_length=45, min_length=1)
    role = mongo.db.EnumField(mongo.db.StringField('SERVICE', 'SUPPORT'))
    shift_hours = mongo.db.FloatField(max_value=9, min_value = 0)
    tip_hours = mongo.db.FloatField(max_value = 9, min_value = 0)
    cash_tips = mongo.db.FloatField(max_value=5000, min_value=0)
    cc_tips = mongo.db.FloatField(max_value=5000, min_value=0)

    def full_name(self) -> str:
        name = self.first_name + ' ' + self.last_name
        return name



class Shift(mongo.db.Document):
    staff = mongo.db.ListField(Employee)
    cc_tip_pool = mongo.db.FloatField(max_value=50000, min_value=0)
    cash_subtotals = mongo.db.DictField(value_type=mongo.db.FloatField)
    shift_hours = mongo.db.FloatField(max_value=100, min_value=0)
    tip_hours = mongo.db.FloatField(max_value=100, min_value=0)
    cash_tip_wage = mongo.db.FloatField(max_value=100, min_value=0)
    cc_tip_wage = mongo.mongo.db.FloatField(max_value=100, min_value=0)
    start_date = mongo.db.DateTimeField(min_date=datetime(2018,12,31,0,0,0), use_tz=pytz.timezone('US/Central'))
    cash_tip_pool = mongo.db.FloatField(max_value=50000, min_value=0)

