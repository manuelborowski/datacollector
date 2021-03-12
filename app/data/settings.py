from flask_login import current_user
from app.data.models import Settings
from app import log
from app import db
import datetime


# return: found, value
# found: if True, setting was found else not
# value ; if setting was found, returns the value
def get_setting(name, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_INT:
            value = int(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_FLOAT:
            value = float(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = setting.value == 'True'
        elif setting.type == Settings.SETTING_TYPE.E_DATETIME:
            value = datetime.datetime.strptime(setting.value, '%Y-%m-%d %H:%M:%S:%f')
        else:
            value = setting.value
    except:
        return False, ''
    return True, value


def add_setting(name, value, type, id=-1):
    setting = Settings(name=name, value='', type=type, user_id=id if id > -1 else current_user.id)
    db.session.add(setting)
    set_setting(name, value, id)
    log.info('add: {}'.format(setting.log()))
    return True


def set_setting(name, value, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_DATETIME:
            setting.value = value.strftime('%Y-%m-%d %H:%M:%S:%f')
        else:
            setting.value = str(value)
        db.session.commit()
    except:
        return False
    return True


def get_test_server():
    found, value = get_setting('test_server', 1)
    if found: return value
    add_setting('test_server', False, Settings.SETTING_TYPE.E_BOOL, 1)
    return False


default_configuration_settings = {
    'register-template': ('', Settings.SETTING_TYPE.E_STRING),
    'register-message-ack-subject-template': ('', Settings.SETTING_TYPE.E_STRING),
    'register-message-ack-content-template': ('', Settings.SETTING_TYPE.E_STRING),

    'registration-timeslot-template': ('', Settings.SETTING_TYPE.E_STRING),

    'message-send-max-retries': (2, Settings.SETTING_TYPE.E_INT),
    'message-task-interval': (10, Settings.SETTING_TYPE.E_INT),
    'messages-per-minute': (30, Settings.SETTING_TYPE.E_INT),
    'base-url': ('localhost:5000', Settings.SETTING_TYPE.E_STRING),
    'enable-send-message': (False, Settings.SETTING_TYPE.E_BOOL),
}


def get_configuration_settings():
    configuration_settings = {}
    for k in default_configuration_settings:
        configuration_settings[k] = get_configuration_setting(k)
    return configuration_settings


def set_configuration_setting(setting, value):
    if value == None:
        value = default_configuration_settings[setting][0]
    return set_setting(setting, value, 1)


def get_configuration_setting(setting):
    found, value = get_setting(setting, 1)
    if found:
        return value
    else:
        default_setting = default_configuration_settings[setting]
        add_setting(setting, default_setting[0], default_setting[1], 1)
        return default_setting[0]
