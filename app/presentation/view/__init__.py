from app.application import register as mregister, timeslot as mtimeslot
from app import flask_app
import json, re

false = False
true = True
null = None


def prepare_registration_form(data):
    ret = mregister.get_default_values(data)
    if ret.code == ret.Result.E_OK:
        if 'timeslots' in ret.result:
            update_timeslots(ret.result['timeslots'], ret.result['template'], 'radio-contact-timeslots')
    return ret


def update_timeslots(timeslots, form, key):
    components = form['components']
    for component in components:
        if 'key' in component and component['key'] == key:
            value_template = component['values'][0]
            component['values'] = []
            for timeslot in timeslots:
                new_value = dict(value_template)
                new_value['label'] = timeslot['label']
                new_value['value'] = timeslot['value']
                component['values'].append(new_value)
            return
        if 'components' in component:
            update_timeslots(timeslots, component, key)
    return


def prepare_timeslot_form():
    ret = mtimeslot.get_default_values()
    return ret
