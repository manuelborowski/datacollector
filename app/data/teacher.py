from app import db, log
from app.data import utils as mutils
from app.data.models import Person
import json


def add_teacher(name=None, user_name=None, badge=None, smartschool_id=None, smartschool_flags=None, data=None,
                enabled=True):
    try:
        teacher = add_bulk_teacher(name=name, user_name=user_name, badge=badge, smartschool_id=smartschool_id,
                                   smartschool_flags=smartschool_flags, data=data, enabled=enabled)
        db.session.commit()
        return teacher
    except Exception as e:
        mutils.raise_error('could not add teacher', e)
    return None


def add_bulk_teacher(name=None, user_name=None, badge=None, smartschool_id=None, smartschool_flags=None, data=None,
                     enabled=True):
    try:
        teacher = Person(full_name=name, user_name=user_name, badge_code=badge, smartschool_id=smartschool_id,
                         smartschool_flags=smartschool_flags, enabled=enabled, data=data)
        db.session.add(teacher)
        return teacher
    except Exception as e:
        mutils.raise_error('could not add bulk teacher', e)
    return None


def end_add_bulk_teacher():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end add bulk teacher', e)
    return None


def update_teacher(teacher, name=None, user_name=None, badge=None, smartschool_id=None, smartschool_flags=None, data=None,
                enabled=True):
    try:
        teacher = update_bulk_teacher(teacher, name=name, user_name=user_name, badge=badge, smartschool_id=smartschool_id,
                                   smartschool_flags=smartschool_flags, data=data, enabled=enabled)
        db.session.commit()
        return teacher
    except Exception as e:
        mutils.raise_error('could not edit teacher', e)
    return None


def update_bulk_teacher(teacher, name=None, user_name=None, badge=None, smartschool_id=None, smartschool_flags=None, data=None,
                     enabled=None):
    try:
        if name:
            teacher.name = name
        if user_name:
            teacher.user_name = user_name
        if badge:
            teacher.badge_code = badge
        if smartschool_id:
            teacher.smartschool_id = smartschool_id
        if smartschool_flags:
            teacher.smartschool_flags = smartschool_flags
        if data:
            teacher.data = data
        if enabled is not None:
            teacher.enabled = enabled
        return teacher
    except Exception as e:
        mutils.raise_error('could not edit bulk teacher', e)
    return None


def end_update_bulk_teacher():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end update bulk teacher', e)
    return None


def get_teachers(enabled=None, first=False):
    try:
        teachers = Person.query
        if enabled is not None:
            teachers = teachers.filter(Person.enabled == enabled)
        if first:
            teacher = teachers.first()
            return teacher
        teachers = teachers.all()
        return teachers
    except Exception as e:
        mutils.raise_error('could not get teachers', e)
    return None


def get_first_teacher(enabled=None):
    return get_teachers(enabled=enabled, first=True)




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
