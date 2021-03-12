from app import log
from app.data import registration as mregistration, settings as msettings, timeslot as mtimeslot, utils as mutils
from app.application import smartschool as msmartschool
import json


def send_ack_message(**kwargs):
    try:
        registration = mregistration.get_first_registration(ack_sent=False, enabled=True)
        if registration:
            message_send_max_retries = msettings.get_configuration_setting('message-send-max-retries')
            if registration.ack_send_retry >= message_send_max_retries:
                mregistration.set_enabled(registration, False)
                return
            mregistration.update_registration(registration, ack_send_retry=registration.ack_send_retry + 1)
            flat = registration.ret_flat()
            data = json.loads(flat['data'])
            to_id = registration.student_id
            to_nbr_coaccount = data['nbr_coaccount']
            timeslot = registration.timeslot.ret_formio()
            timeslot_string = mutils.datetime_to_dutch_datetime_string(timeslot['timeslot-date'])
            url = timeslot['timeslot-meeting-url']

            message_subject = msettings.get_configuration_setting('register-message-ack-subject-template')
            message_content = msettings.get_configuration_setting('register-message-ack-content-template')

            message_subject = message_subject.replace('{{TAG-TIMESLOT}}', timeslot_string)
            message_content = message_content.replace('{{TAG-TIMESLOT}}', timeslot_string)
            message_content = message_content.replace('{{TAG-MEETING-URL}}', f'<a href="{url}" target="_blank">deze link</a>')

            log.info(f'{message_subject} to {to_id}/{to_nbr_coaccount}')
            ret = msmartschool.send_message(to_id, to_nbr_coaccount, message_subject, message_content)
            if ret:
                mregistration.set_ack_sent(registration, True)
            return ret
        return False
    except Exception as e:
        log.error(f'Could not send message {e}')
    return False

msmartschool.subscribe_send_message(send_ack_message, {})


class RegisterResult:
    def __init__(self, code, result=None):
        self.code = code
        self.result = result

    class Result:
        E_OK = 'ok'
        E_ERROR = 'error'
        E_COULD_NOT_REGISTER = 'could-not-register'

    code = Result.E_OK
    result = {}


def get_default_values(data):
    try:
        timeslots = []
        available_timeslots = mtimeslot.get_free_timeslots()
        for timeslot in available_timeslots:
            timeslots.append({
                'label': mutils.datetime_to_dutch_datetime_string(timeslot.date),
                'value': timeslot.id
            })
        template = json.loads(msettings.get_configuration_setting('register-template'))
        hidden_data = json.dumps({
            'student-id': data['id'],
            'nbr-coaccount': data['nbr_coaccount']
        })
        formio_data = {
            'student-name': f'{data["student_first_name"]} {data["student_last_name"]}',
            'parent-name': f'{data["parent_first_name"]} {data["parent_last_name"]}',
            'hidden-data': hidden_data
        }
        ret = {
            'timeslots': timeslots,
            'template': template,
            'formio_data': formio_data
        }
        return RegisterResult(RegisterResult.Result.E_OK, ret)
    except Exception as e:
        log.error(f'Could not get default values {e}')
    return RegisterResult(RegisterResult.Result.E_ERROR)


def add_or_update_registration(data):
    try:
        hidden_data = json.loads(data['hidden-data'])
        registration = mregistration.get_first_registration(student_id=hidden_data['student-id'])
        timeslot = mtimeslot.get_first_timeslot(id=data['radio-contact-timeslots'])
        if registration:
            mregistration.update_registration(registration, timeslot=timeslot, ack_send_retry=0)
            mregistration.set_ack_sent(registration, False)
            mregistration.set_enabled(registration, True)
        else:
            registration = mregistration.add_registration(hidden_data['student-id'], data['student-name'],
                                                          data['parent-name'], hidden_data['nbr-coaccount'], timeslot)
        timeslot_string = mutils.datetime_to_dutch_datetime_string(registration.timeslot.date)
        return RegisterResult(RegisterResult.Result.E_OK, {'timeslot': timeslot_string})
    except Exception as e:
        log.error(f'Could not add or update registration {e}')
        return RegisterResult(RegisterResult.Result.E_COULD_NOT_REGISTER)
    return RegisterResult(RegisterResult.Result.E_ERROR)


def delete_registration(id_list):
    return mregistration.delete_registrations(id_list=id_list)