from app.data import settings as msettings
from app.application import utils as mutils


def get_configuration_settings():
    return msettings.get_configuration_settings()


def set_configuration_setting(setting, value):
    msettings.set_configuration_setting(setting, value)


def set_setting_topic(settings):
    try:
        for k, container in settings.items():
            if 'submit' in container and container['submit']:
                for key, value in container.items():
                    if key in handle_set_topic:
                        handle_set_topic[key]['cb'](key, value, handle_set_topic[key]['opaque'])
                    else:
                        msettings.set_configuration_setting(key, value)
    except Exception as e:
        mutils.raise_error('Could not set settings topic', e)


handle_set_topic = {}


def subscribe_handle_set_topic(topic, cb, opaque):
    handle_set_topic[topic] = {
        'cb': cb,
        'opaque': opaque
    }