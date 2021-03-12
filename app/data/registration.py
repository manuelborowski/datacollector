from app import db, log
from app.data import utils as mutils, timeslot as mtimeslot
from app.data.models import Registration, Timeslot
import json


ack_sent_cb = []


def set_ack_sent(registration, value):
    registration.ack_sent = value
    db.session.commit()
    for cb in ack_sent_cb:
        cb[0](value, cb[1])
    return True


def subscribe_ack_sent(cb, opaque):
    ack_sent_cb.append((cb, opaque))
    return True


enabled_cb = []


def set_enabled(registration, value):
    registration.enabled = value
    db.session.commit()
    for cb in enabled_cb:
        cb[0](value, cb[1])
    return True


def subscribe_enabled(cb, opaque):
    enabled_cb.append((cb, opaque))
    return True


def add_registration(student_id, student_name, parent_name, nbr_coaccount, timeslot):
    try:
        data = json.dumps({
            'student_name': student_name,
            'parent_name': parent_name,
            'nbr_coaccount': nbr_coaccount
        })
        registration = Registration(student_id=student_id, data=data, timeslot=timeslot)
        db.session.add(registration)
        db.session.commit()
        return registration
    except Exception as e:
        mutils.raise_error('could not add registration', e)
    return None


def update_registration(registration, timeslot=None, ack_send_retry=None):
    try:
        if timeslot:
            registration.timeslot = timeslot
        if ack_send_retry is not None:
            registration.ack_send_retry = ack_send_retry
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not update registration', e)


def get_registrations(id=None, student_id=None, ack_sent=None, enabled=None, first=False):
    try:
        registrations = Registration.query
        if id:
            registrations = registrations.filter(Registration.id == id)
        if student_id:
            registrations = registrations.filter(Registration.student_id == student_id)
        if ack_sent is not None:
            registrations = registrations.filter(Registration.ack_sent == ack_sent)
        if enabled is not None:
            registrations = registrations.filter(Registration.enabled == enabled)
        if first:
            registration = registrations.first()
            return registration
        registrations = registrations.all()
        return registrations
    except Exception as e:
        mutils.raise_error('could not get registrations', e)
    return None


def get_first_registration(id=None, student_id=None, ack_sent=None, enabled=None):
    return get_registrations(id=id, student_id=student_id, ack_sent=ack_sent, enabled=enabled, first=True)


def delete_registrations(id=None, id_list=None):
    try:
        if id:
            id_list = [id]
        for i in id_list:
            registration = get_first_registration(id=int(i))
            db.session.delete(registration)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not remove registrations', e)
    return []



def pre_filter():
    return Registration.query.join(Timeslot)

def format_data(db_list):
    out = []
    for i in db_list:
        em = json.loads(i.data)
        em.update(i.ret_datatable())
        em['timeslot-date'] = mutils.datetime_to_dutch_datetime_string(em['timeslot-date'])
        em['timeslot-meeting-url'] = f'<a href="{em["timeslot-meeting-url"]}" target="_blank">Link naar meeting</a>'
        em['row_action'] = f"{i.id}"
        out.append(em)
    return out

