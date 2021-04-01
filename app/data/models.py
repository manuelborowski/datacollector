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


class Person(db.Model):
    __tablename__ = 'persons'

    FLAG_ALL_1_MASK = (1 << 32) - 1

    NEW_FLAG =                  1 << 0
    UPDATED_FLAG =              1 << 1
    ENABLED_FLAG =              1 << 2 # short term enable/disable of a person
    ACTIVE_FLAG =               1 << 3 # long term enable/disable of a person
    IS_TEACHER_FLAG =           1 << 4 # this is an original teacher
    IS_SUB_TEACHER_FLAG =       1 << 5 # this is a substitute teacher
    IS_INTERN_TEACHER_FLAG =    1 << 6 # this is an intern teacher
    IS_DIRECTOR_FLAG =          1 << 7
    IS_STAFF_FLAG =             1 << 8
    IS_STUDENT_FLAG =           1 << 9

    ROLE_GROUP = IS_TEACHER_FLAG | IS_STUDENT_FLAG
    flag_to_role = {
        IS_TEACHER_FLAG: 'teacher',
        IS_STUDENT_FLAG: 'student'
    }

    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(256))

    ad_user_name = db.Column(db.String(256))

    rfid_code = db.Column(db.String(256))

    ss_user_name = db.Column(db.String(256))
    ss_internal_nbr = db.Column(db.String(256))

    flags = db.Column(db.Integer(), default=0)

    data = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def set_flag(self, flag, value):
        if value:
            self.flags |= flag
        else:
            self.flags &= (Person.FLAG_ALL_1_MASK ^ flag)

    def get_role(self):
        role = self.flags & Person.ROLE_GROUP
        return Person.flag_to_role[role]

    def is_new(self):
        return bool(self.flags & Person.NEW_FLAG)

    def is_updated(self):
        return bool(self.flags & Person.UPDATED_FLAG)

    def data_table(self):
        return {'name': self.full_name, 'ss_user_name': self.ss_user_name, 'ad_user_name': self.ad_user_name,
                'ss_internal_nbr': self.ss_internal_nbr, 'rfid': self.rfid_code,
                'role': self.get_role(), 'new': self.is_new(), 'updated': self.is_updated()}


