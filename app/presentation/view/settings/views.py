from flask import render_template, url_for, request
from flask_login import login_required
from app import admin_required
from app.application import socketio as msocketio, timeslot as mtimeslot
from . import settings
from app.application import settings as msettings
import json


@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    timeslots = mtimeslot.get_timeslots()
    data = {
        'default': default_settings,
        'template': settings_formio,
        'timeslots': timeslots,
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
                "key": "guest-container",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "BEZOEKERS : Registratie en smartschoolbericht template",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate1",
                        "type": "panel",
                        "label": "BEZOEKERS : Registratie template en e-mail",
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
                                "label": "contactmoment registratie template",
                                "autoExpand": false,
                                "tableView": true,
                                "key": "register-template",
                                "type": "textarea",
                                "input": true
                            },
                            {
                                "label": "Registratie bevestigingsbericht: onderwerp",
                                "autoExpand": false,
                                "tableView": true,
                                "persistent": false,
                                "key": "register-message-ack-subject-template",
                                "type": "textarea",
                                "input": true
                            },
                            {
                                "label": "Registratie bevestigingsbericht: inhoud",
                                "autoExpand": false,
                                "tableView": true,
                                "persistent": false,
                                "key": "register-message-ack-content-template",
                                "type": "textarea",
                                "input": true
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Timeslots",
                "tableView": false,
                "key": "timeslot-container",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Tijdsloten",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate2",
                        "type": "panel",
                        "label": "BEZOEKERS : Registratie en smartschoolbericht template",
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
                                "label": "Tijdslot template",
                                "autoExpand": false,
                                "tableView": true,
                                "key": "registration-timeslot-template",
                                "type": "textarea",
                                "input": true
                            },
                            {
                                "label": "Tijdsloten",
                                "reorder": false,
                                "addAnotherPosition": "bottom",
                                "defaultOpen": false,
                                "layoutFixed": false,
                                "enableRowGroups": false,
                                "initEmpty": false,
                                "tableView": false,
                                "defaultValue": [
                                    {}
                                ],
                                "key": "timeslot-list",
                                "type": "datagrid",
                                "input": true,
                                "components": [
                                    {
                                        "label": "Tijdslot",
                                        "format": "dd-MM-yyyy HH:mm",
                                        "tableView": false,
                                        "enableMinDateInput": false,
                                        "datePicker": {
                                            "disableWeekends": false,
                                            "disableWeekdays": false
                                        },
                                        "enableMaxDateInput": false,
                                        "timePicker": {
                                            "showMeridian": false,
                                            "minuteStep": 15
                                        },
                                        "persistent": false,
                                        "key": "timeslot-date",
                                        "type": "datetime",
                                        "input": true,
                                        "widget": {
                                            "type": "calendar",
                                            "displayInTimezone": "viewer",
                                            "locale": "en",
                                            "useLocaleSettings": false,
                                            "allowInput": true,
                                            "mode": "single",
                                            "enableTime": true,
                                            "noCalendar": false,
                                            "format": "dd-MM-yyyy HH:mm",
                                            "hourIncrement": 1,
                                            "minuteIncrement": 15,
                                            "time_24hr": true,
                                            "minDate": null,
                                            "disableWeekends": false,
                                            "disableWeekdays": false,
                                            "maxDate": null
                                        }
                                    },
                                    {
                                        "label": "Meeting URL",
                                        "tableView": true,
                                        "key": "timeslot-meeting-url",
                                        "type": "textfield",
                                        "input": true
                                    },
                                    {
                                        "label": "Actief",
                                        "tableView": false,
                                        "key": "timeslot-enabled",
                                        "type": "checkbox",
                                        "input": true,
                                        "defaultValue": false
                                    },
                                    {
                                        "label": "Number",
                                        "hidden": true,
                                        "mask": false,
                                        "spellcheck": true,
                                        "tableView": false,
                                        "delimiter": false,
                                        "requireDecimal": false,
                                        "inputFormat": "plain",
                                        "key": "timeslot-id",
                                        "type": "number",
                                        "input": true
                                    },
                                    {
                                        "label": "Action",
                                        "defaultValue": "N",
                                        "key": "timeslot-action",
                                        "type": "hidden",
                                        "input": true,
                                        "tableView": false
                                    }
                                ]
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Smartschool",
                "tableView": false,
                "key": "smartschool-container",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Smartschoolbericht server settings",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "eMailServerSettings",
                        "type": "panel",
                        "label": "E-mail server settings",
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
                                "label": "Aantal keer dat een bericht geprobeerd wordt te verzenden",
                                "labelPosition": "left-left",
                                "mask": false,
                                "spellcheck": false,
                                "tableView": false,
                                "delimiter": false,
                                "requireDecimal": false,
                                "inputFormat": "plain",
                                "key": "message-send-max-retries",
                                "type": "number",
                                "input": true
                            },
                            {
                                "label": "Tijd (seconden) tussen het verzenden van berichten",
                                "labelPosition": "left-left",
                                "mask": false,
                                "spellcheck": true,
                                "tableView": false,
                                "persistent": false,
                                "delimiter": false,
                                "requireDecimal": false,
                                "inputFormat": "plain",
                                "key": "message-task-interval",
                                "type": "number",
                                "input": true
                            },
                            {
                                "label": "Max aantal berichten per minuut",
                                "labelPosition": "left-left",
                                "mask": false,
                                "spellcheck": true,
                                "tableView": false,
                                "persistent": false,
                                "delimiter": false,
                                "requireDecimal": false,
                                "inputFormat": "plain",
                                "key": "messages-per-minute",
                                "type": "number",
                                "input": true
                            },
                            {
                                "label": "Basis URL",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "key": "base-url",
                                "type": "textfield",
                                "input": true
                            },
                            {
                                "label": "Berichten mogen worden verzonden",
                                "tableView": false,
                                "defaultValue": false,
                                "persistent": false,
                                "key": "enable-send-message",
                                "type": "checkbox",
                                "input": true
                            }
                        ],
                        "collapsed": true
                    }
                ]
            }
        ]
    }
