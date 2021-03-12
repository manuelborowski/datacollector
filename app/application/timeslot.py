from app.data import settings as msettings, timeslot as mtimeslot, utils as mutils
from app.application.settings import subscribe_handle_set_topic
from app import log
import json



def get_default_values():
    try:
        timeslot_template = json.loads(msettings.get_configuration_setting('registration-timeslot-template'))
        timeslots_data = get_timeslots()
        ret = {
            'template': timeslot_template,
            'timeslots': timeslots_data
        }
        return ret
    except Exception as e:
        mutils.raise_error(f'could not get default timeslot values', e)
    return None


def get_timeslots():
    try:
        timeslots = mtimeslot.get_timeslots()
        timeslots_data = []
        for timeslot in timeslots:
            formio = timeslot.ret_formio()
            formio['timeslot-date'] = mutils.datetime_to_formiodate(formio['timeslot-date'])
            timeslots_data.append(formio)
        return timeslots_data
    except Exception as e:
        mutils.raise_error(f'could not get timeslots', e)
    return None



def set_timeslots(topic, data, opaque):
    try:
        timeslot_ids = mtimeslot.get_timeslot_ids()
        for entry in data:
            if entry['timeslot-action'] == 'N':
                date = mutils.formiodate_to_datetime(entry['timeslot-date'])
                timeslot = mtimeslot.add_timeslot(date, entry['timeslot-meeting-url'], entry['timeslot-enabled'])
            elif entry['timeslot-action'] == 'U':
                timeslot = mtimeslot.get_first_timeslot(entry['timeslot-id'])
                date = mutils.formiodate_to_datetime(entry['timeslot-date'])
                mtimeslot.update_timeslot(timeslot, date, entry['timeslot-meeting-url'], entry['timeslot-enabled'])
                timeslot_ids.remove(int(entry['timeslot-id']))
            elif entry['timeslot-action'] == 'V':
                timeslot_ids.remove(int(entry['timeslot-id']))
        if timeslot_ids:
            mtimeslot.delete_timeslots(id_list=timeslot_ids)
    except Exception as e:
        log.error(f'could not set timeslots: {e}')


subscribe_handle_set_topic('timeslot-list', set_timeslots, None)