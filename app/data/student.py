from app import db, log
from app.data import utils as mutils
from app.data.models import Student
import json


def add_student(name=None, ss_user_name=None, ad_user_name=None, badge=None, data=None, wisa_nbr=None, enabled=True):
    try:
        student = add_bulk_student(name=name, ss_user_name=ss_user_name, ad_user_name=ad_user_name, badge=badge, wisa_nbr=wisa_nbr,
                          enabled=enabled, data=data)
        db.session.commit()
        return student
    except Exception as e:
        mutils.raise_error('could not add student', e)
    return None


def add_bulk_student(name=None, ss_user_name=None, ad_user_name=None, badge=None, data=None, wisa_nbr=None, enabled=True):
    try:
        student = Student(full_name=name, ss_user_name=ss_user_name, ad_user_name=ad_user_name, badge_code=badge, wisa_nbr=wisa_nbr,
                          enabled=enabled, data=data)
        db.session.add(student)
        return student
    except Exception as e:
        mutils.raise_error('could not add bulk student', e)
    return None


def end_add_bulk_student():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end add bulk student', e)
    return None


def update_student(student, name=None, ss_user_name=None, ad_user_name=None, badge=None, data=None, wisa_nbr=None, enabled=None):
    try:
        student = update_bulk_student(student, name=name, ss_user_name=ss_user_name, ad_user_name=ad_user_name, badge=badge, wisa_nbr=wisa_nbr,
                          enabled=enabled, data=data)
        db.session.commit()
        return student
    except Exception as e:
        mutils.raise_error('could not edit student', e)
    return None


def update_bulk_student(student, name=None, ss_user_name=None, ad_user_name=None, badge=None, data=None, wisa_nbr=None, enabled=None):
    try:
        if name:
            student.name = name
        if ss_user_name:
            student.ss_user_name = ss_user_name
        if ad_user_name:
            student.ad_user_name = ad_user_name
        if badge:
            student.badge_code = badge
        if wisa_nbr:
            student.wisa_nbr = wisa_nbr
        if data:
            student.data = data
        if enabled is not None:
            student.enabled = enabled
        return student
    except Exception as e:
        mutils.raise_error('could not edit bulk student', e)
    return None


def end_update_bulk_student():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end update bulk student', e)
    return None


def get_students(enabled=None, first=False):
    try:
        students = Student.query
        if enabled is not None:
            students = students.filter(Student.enabled == enabled)
        if first:
            student = students.first()
            return student
        students = students.all()
        return students
    except Exception as e:
        mutils.raise_error('could not get students', e)
    return None


def get_first_student(enabled=None):
    return get_students(enabled=enabled, first=True)




# def pre_filter():
#     return Registration.query.join(Timeslot)
#
#
# def format_data(db_list):
#     out = []
#     for i in db_list:
#         em = json.loads(i.data)
#         em.update(i.ret_datatable())
#         em['timeslot-date'] = mutils.datetime_to_dutch_datetime_string(em['timeslot-date'])
#         em['timeslot-meeting-url'] = f'<a href="{em["timeslot-meeting-url"]}" target="_blank">Link naar meeting</a>'
#         em['row_action'] = f"{i.id}"
#         out.append(em)
#     return out
