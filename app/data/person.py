from app import db, log
from app.data import utils as mutils
from app.data.models import Person
import json


class ROLE:
    TEACHER = Person.IS_TEACHER_FLAG
    STUDENT = Person.IS_STUDENT_FLAG
    DIRECTOR = Person.IS_DIRECTOR_FLAG
    STAFF = Person.IS_STAFF_FLAG


def add_person(full_name=None, ad_user_name=None, rfid_code=None, ss_user_name=None, ss_internal_nbr=None,
               role=None, data=None):
    try:
        person = add_bulk_person(full_name=full_name, ad_user_name=ad_user_name, rfid_code=rfid_code,
                                 ss_user_name=ss_user_name, ss_internal_nbr=ss_internal_nbr,
                                 role=role, data=data)
        db.session.commit()
        return person
    except Exception as e:
        mutils.raise_error('could not add person', e)
    return None


def add_bulk_person(full_name=None, ad_user_name=None, rfid_code=None, ss_user_name=None, ss_internal_nbr=None,
                    role=None, data=None):
    try:
        flags = role | Person.ACTIVE_FLAG | Person.ENABLED_FLAG | Person.UPDATED_FLAG
        person = Person(full_name=full_name,
                        ad_user_name=ad_user_name,
                        rfid_code=rfid_code,
                        ss_user_name=ss_user_name,
                        ss_internal_nbr=ss_internal_nbr,
                        flags=flags,
                        data=data)
        db.session.add(person)
        return person
    except Exception as e:
        mutils.raise_error('could not add bulk person', e)
    return None


def end_add_bulk_person():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end add bulk person', e)
    return None


def update_person(person, full_name=None, ad_user_name=None, rfid_code=None, ss_user_name=None, ss_internal_nbr=None,
                enabled=None, active=None, updated=True, data=None):
    try:
        person = update_bulk_person(person, full_name=full_name, ad_user_name=ad_user_name, rfid_code=rfid_code,
                                    ss_user_name=ss_user_name, ss_internal_nbr=ss_internal_nbr,
                                    enabled=enabled, active=active, updated=updated, data=data)
        db.session.commit()
        return person
    except Exception as e:
        mutils.raise_error('could not edit person', e)
    return None


def update_bulk_person(person, full_name=None, ad_user_name=None, rfid_code=None, ss_user_name=None, ss_internal_nbr=None,
                enabled=None, active=None, updated=True, data=None):
    try:
        if full_name:
            person.name = full_name
        if ad_user_name:
            person.ad_user_name = ad_user_name
        if rfid_code:
            person.rfid_code = rfid_code
        if ss_user_name:
            person.ss_user_name = ss_user_name
        if ss_internal_nbr:
            person.ss_internal_nbr = ss_internal_nbr
        if data:
            person.data = data
        if enabled is not None:
            person.set_flag(Person.ENABLED_FLAG, enabled)
        if active is not None:
            person.set_flag(Person.ACTIVE_FLAG, active)
        if updated is not None:
            person.set_flag(Person.UPDATED_FLAG, updated)
        return person
    except Exception as e:
        mutils.raise_error('could not edit bulk person', e)
    return None


def end_update_bulk_person():
    try:
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not end update bulk person', e)
    return None


def get_persons(enabled=None, active=None, updated=None, role=None, first=False, count=False):
    try:
        persons = Person.query
        if enabled is not None:
            if enabled:
                persons = persons.filter(Person.flags.op('&')(Person.ENABLED_FLAG))
            else:
                persons = persons.filter(~Person.flags.op('&')(Person.ENABLED_FLAG))
        if active is not None:
            if active:
                persons = persons.filter(Person.flags.op('&')(Person.ACTIVE_FLAG))
            else:
                persons = persons.filter(~Person.flags.op('&')(Person.ACTIVE_FLAG))
        if updated is not None:
            if updated:
                persons = persons.filter(Person.flags.op('&')(Person.UPDATED_FLAG))
            else:
                persons = persons.filter(~Person.flags.op('&')(Person.UPDATED_FLAG))
        if role:
            persons = persons.filter(Person.flags.op('&')(role))
        if first:
            person = persons.first()
            return person
        elif count:
            nbr = persons.count()
            return nbr
        persons = persons.all()
        return persons
    except Exception as e:
        mutils.raise_error('could not get persons', e)
    return None


def get_first_person(enabled=None, active=None, updated=None, role=None):
    return get_persons(enabled=enabled,active=active, updated=updated, role=role, first=True)


def get_person_count(enabled=None, active=None, updated=None, role=None):
    return get_persons(enabled=enabled,active=active, updated=updated, role=role, count=True)


def enable_flag(person, value):
    person.set_flag(Person.ENABLED_FLAG, value)


def activate_person(person, value):
    person.set_flag(Person.ACTIVE_FLAG, value)


def update_flag(person, value):
    person.set_flag(Person.UPDATED_FLAG, value)


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
