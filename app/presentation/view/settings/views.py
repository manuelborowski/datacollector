from flask import render_template, url_for, request
from flask_login import login_required
from app import admin_required
from app.application import socketio as msocketio
from . import settings
from app.application import settings as msettings
import json


@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    data = {
        'default': default_settings,
        'template': settings_formio,
    }
    return render_template('/settings/settings.html', data=data)


def update_settings_cb(msg, client_sid=None):
    try:
        data = msg['data']
        settings = json.loads(data['value'])
        msettings.set_setting_topic(settings)
        msettings.set_configuration_setting(data['setting'], data['value'])
        msocketio.send_to_room({'type': 'settings', 'data': {'status': True}}, client_sid)
    except Exception as e:
        msocketio.send_to_room({'type': 'settings', 'data': {'status': False, 'message': str(e)}}, client_sid)


msocketio.subscribe_on_type('settings', update_settings_cb)

from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
    {
        "display": "form",
        "components": [
            {
                "label": "Guest",
                "tableView": false,
                "key": "settings-container",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Smartschool",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate1",
                        "type": "panel",
                        "label": "Smartschool",
                        "input": false,
                        "tableView": false,
                        "components": [
                            {
                                "label": "Submit",
                                "showValidations": false,
                                "theme": "warning",
                                "tableView": false,
                                "key": "submit",
                                "type": "button",
                                "input": true
                            },
                            {
                                "label": "When to update database (https://crontab.guru/)",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-scheduler-cron",
                                "type": "textfield",
                                "input": true
                            },
                            {
                                "label": "Teacher groupname",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-teacher-group",
                                "type": "textfield",
                                "input": true
                            },
                            {
                                "label": "WebAPI URL",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-api-url",
                                "type": "textfield",
                                "input": true
                            },
                            {
                                "label": "WebAPI Key",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-api-key",
                                "type": "textfield",
                                "input": true
                            }
                        ],
                        "collapsed": true
                    }
                ]
            }
        ]
    }