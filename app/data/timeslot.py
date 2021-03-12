from app.data.models import Timeslot, Registration
from app.data import utils as mutils
from app import log, db

def add_timeslot(date=None, meeting_url=None, enabled=None):
    try:
        if date and meeting_url and enabled:
            timeslot = Timeslot(date=date, length=30, meeting_url=meeting_url, enabled=enabled)
            db.session.add(timeslot)
            db.session.commit()
            log.info(f'added timeslot: {date}')
            return timeslot
    except Exception as e:
        mutils.raise_error('could add timeslot', e)
    return None


def update_timeslot(timeslot, date=None, meeting_url=None, enabled=None):
    try:
        if date is not None:
            timeslot.date = date
        if meeting_url is not None:
            timeslot.meeting_url = meeting_url
        if enabled is not None:
            timeslot.enabled = enabled
        db.session.commit()
        return timeslot
    except Exception as e:
        mutils.raise_error('could update timeslot', e)
    return None


def get_timeslots(id=None, first=False):
    try:
        timeslots = Timeslot.query
        if id:
            timeslots = timeslots.filter(Timeslot.id == id)
        if first:
            timeslot = timeslots.first()
            return timeslot
        timeslots = timeslots.order_by(Timeslot.date).all()
        return timeslots
    except Exception as e:
        mutils.raise_error('could not get timeslots', e)
    return None


def get_first_timeslot(id=None):
    return get_timeslots(id=id, first=True)


# return all timeslots where there is no Registration referring to it.
def get_free_timeslots():
    try:
        timeslots = Timeslot.query.join(Registration, isouter=True).filter(Registration.id==None)
        timeslots = timeslots.all()
        return timeslots
    except Exception as e:
        mutils.raise_error('could not get free timeslots', e)
    return None


def get_timeslot_ids():
    try:
        timeslot_ids = [t.id for t in db.session.query(Timeslot.id)]
        return timeslot_ids
    except Exception as e:
        mutils.raise_error('could not get timeslot ids', e)
    return []


def delete_timeslots(id=None, id_list=None):
    try:
        if id:
            id_list = [id]
        for i in id_list:
            timeslot = get_first_timeslot(i)
            db.session.delete(timeslot)
        db.session.commit()
    except Exception as e:
        mutils.raise_error('could not remove timeslots', e)
    return []


