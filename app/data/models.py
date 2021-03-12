from app import log, db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint
import inspect, datetime, babel
from flask import url_for
from sqlalchemy.sql import func
from sqlalchemy.orm import column_property
from babel.dates import get_day_names, get_month_names


def datetime_to_dutch_date_string(date):
    return babel.dates.format_date(date, locale='nl')


# woensdag 24 februari om 14 uur
def datetime_to_dutch_datetime_string(date):
    date_string = f'{get_day_names(locale="nl")[date.weekday()]} {date.day} {get_month_names(locale="nl")[date.month]} om {date.strftime("%H.%M")} uur'
    return date_string

def datetime_to_formiodate(date):
    string = f"{datetime.datetime.strftime(date, '%Y-%m-%dT%H:%M')}:00+01:00"
    return string


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    class USER_TYPE:
        LOCAL = 'local'
        OAUTH = 'oauth'

    @staticmethod
    def get_zipped_types():
        return list(zip(['local', 'oauth'], ['LOCAL', 'OAUTH']))

    class LEVEL:
        USER = 1
        SUPERVISOR = 3
        ADMIN = 5

        ls = ["GEBRUIKER", "GEBRUIKER+", "ADMINISTRATOR"]

        @staticmethod
        def i2s(i):
            if i == 1:
                return User.LEVEL.ls[0]
            elif i == 3:
                return User.LEVEL.ls[1]
            if i == 5:
                return User.LEVEL.ls[2]

    @staticmethod
    def get_zipped_levels():
        return list(zip(["1", "3", "5"], User.LEVEL.ls))

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    username = db.Column(db.String(256))
    first_name = db.Column(db.String(256))
    last_name = db.Column(db.String(256))
    password_hash = db.Column(db.String(256))
    level = db.Column(db.Integer)
    user_type = db.Column(db.String(256))
    last_login = db.Column(db.DateTime())
    settings = db.relationship('Settings', cascade='all, delete', backref='user', lazy='dynamic')

    @property
    def is_local(self):
        return self.user_type == User.USER_TYPE.LOCAL

    @property
    def is_oauth(self):
        return self.user_type == User.USER_TYPE.OAUTH

    @property
    def is_at_least_user(self):
        return self.level >= User.LEVEL.USER

    @property
    def is_strict_user(self):
        return self.level == User.LEVEL.USER

    @property
    def is_at_least_supervisor(self):
        return self.level >= User.LEVEL.SUPERVISOR

    @property
    def is_at_least_admin(self):
        return self.level >= User.LEVEL.ADMIN

    @property
    def password(self):
        raise AttributeError('Paswoord kan je niet lezen.')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        else:
            return True

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    def log(self):
        return '<User: {}/{}>'.format(self.id, self.username)

    def ret_datatable(self):
        return {'id': self.id, 'DT_RowId': self.id, 'email': self.email, 'username': self.username,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'level': User.LEVEL.i2s(self.level), 'user_type': self.user_type, 'last_login': self.last_login,
                'chbx': ''}


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'
        E_DATETIME = 'DATETIME'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(db.Text)
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)


class Teacher(db.Model):
    __tablename__ = 'teachers'

    SS_FLAG_ALL_1_MASK =       (1 << 16) - 1

    SS_TEACHER_FLAG =           1 << 0 # this is an original teacher
    SS_SUB_TEACHER_FLAG =       1 << 1 # this is a substitute teacher
    SS_INTERN_TEACHER_FLAG =    1 << 2 # this is an intern teacher

    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(256))
    user_name = db.Column(db.String(256))
    badge_code = db.Column(db.String(256))

    smartschool_flags = db.Column(db.Integer(), default=0)

    enabled = db.Column(db.Boolean, default=False)

    data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())



