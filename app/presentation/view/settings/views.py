from flask import render_template, url_for, request
from flask_login import login_required
from app import admin_required
from app.application import socketio as msocketio, general as mgeneral
from . import settings
from app.application import settings as msettings, papercut as mpapercut
import json, time


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


def event_received_cb(msg, client_sid=None):
    try:
        ret = {'status': False, 'message': 'unknonw error'}
        event = msg['data']['event']
        if event == 'event-get-teacher-rfid-from-papercut':
            ret = mpapercut.get_rfids()
        elif event == 'event-clear-own-database':
            ret = mgeneral.clear_database()
        elif event == 'event-populate-database':
            ret = mgeneral.populate_database()
        ret['message'] = ret['message'].replace('\n', '<br>')
        msocketio.send_to_room({'type': 'event', 'data': ret}, client_sid)
    except Exception as e:
        msocketio.send_to_room({'type': 'event', 'data': {'status': False, 'message': str(e)}}, client_sid)


msocketio.subscribe_on_type('settings', update_settings_cb)
msocketio.subscribe_on_type('event', event_received_cb)

from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
    {
        "display": "form",
        "components": [
            {
                "label": "General",
                "tableView": false,
                "key": "general",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "General",
                        "theme": "primary",
                        "collapsible": false,
                        "key": "general1",
                        "type": "panel",
                        "label": "General",
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
                                "label": "Do NOT update external databases",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "general-inhibit-update-external-databases",
                                "type": "checkbox",
                                "input": true
                            },
                            {
                                "label": "Table",
                                "cellAlignment": "left",
                                "key": "table",
                                "type": "table",
                                "numRows": 4,
                                "numCols": 2,
                                "input": false,
                                "tableView": false,
                                "rows": [
                                    [
                                        {
                                            "components": [
                                                {
                                                    "label": "Get teacher RFID from Papercut",
                                                    "tableView": false,
                                                    "defaultValue": false,
                                                    "key": "chk-rfid-from-papercut",
                                                    "type": "checkbox",
                                                    "input": true,
                                                    "hideOnChildrenHidden": false
                                                }
                                            ]
                                        },
                                        {
                                            "components": [
                                                {
                                                    "label": "Get teacher RFID from papercut",
                                                    "action": "event",
                                                    "showValidations": false,
                                                    "theme": "warning",
                                                    "tableView": false,
                                                    "key": "getTeacerRfidFromPapercut",
                                                    "conditional": {
                                                        "show": true,
                                                        "when": "general.chk-rfid-from-papercut",
                                                        "eq": "true"
                                                    },
                                                    "type": "button",
                                                    "event": "event-get-teacher-rfid-from-papercut",
                                                    "input": true,
                                                    "hideOnChildrenHidden": false
                                                }
                                            ]
                                        }
                                    ],
                                    [
                                        {
                                            "components": [
                                                {
                                                    "label": "Populate own database (from Smartschool and Papercut). Do this once!",
                                                    "tableView": false,
                                                    "defaultValue": false,
                                                    "key": "chk-populate-database",
                                                    "type": "checkbox",
                                                    "input": true,
                                                    "hideOnChildrenHidden": false
                                                }
                                            ]
                                        },
                                        {
                                            "components": [
                                                {
                                                    "label": "Populate Database",
                                                    "action": "event",
                                                    "showValidations": false,
                                                    "theme": "warning",
                                                    "tableView": false,
                                                    "key": "loadDatabase",
                                                    "conditional": {
                                                        "show": true,
                                                        "when": "general.chk-populate-database",
                                                        "eq": "true"
                                                    },
                                                    "type": "button",
                                                    "event": "event-populate-database",
                                                    "input": true,
                                                    "hideOnChildrenHidden": false
                                                }
                                            ]
                                        }
                                    ],
                                    [
                                        {
                                            "components": [
                                                {
                                                    "label": "Run update cycle now",
                                                    "tableView": false,
                                                    "defaultValue": false,
                                                    "key": "chk-update-database-now",
                                                    "type": "checkbox",
                                                    "input": true
                                                }
                                            ]
                                        },
                                        {
                                            "components": [
                                                {
                                                    "label": "Run update cycle now",
                                                    "action": "event",
                                                    "showValidations": false,
                                                    "theme": "warning",
                                                    "tableView": false,
                                                    "key": "updateDatabaseNow",
                                                    "conditional": {
                                                        "show": true,
                                                        "when": "general.chk-update-database-now",
                                                        "eq": "true"
                                                    },
                                                    "type": "button",
                                                    "event": "event-update-database-now",
                                                    "input": true
                                                }
                                            ]
                                        }
                                    ],
                                    [
                                        {
                                            "components": [
                                                {
                                                    "label": "Clear own database",
                                                    "tableView": false,
                                                    "key": "chk-clear-own-database",
                                                    "type": "checkbox",
                                                    "input": true,
                                                    "defaultValue": false
                                                }
                                            ]
                                        },
                                        {
                                            "components": [
                                                {
                                                    "label": "Clear own database",
                                                    "action": "event",
                                                    "showValidations": false,
                                                    "theme": "danger",
                                                    "tableView": false,
                                                    "key": "clearOwnDatabase",
                                                    "conditional": {
                                                        "show": true,
                                                        "when": "general.chk-clear-own-database",
                                                        "eq": "true"
                                                    },
                                                    "type": "button",
                                                    "event": "event-clear-own-database",
                                                    "input": true
                                                }
                                            ]
                                        }
                                    ]
                                ]
                            }
                        ]
                    }
                ]
            },
            {
                "label": "Cron",
                "tableView": false,
                "key": "cron",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Cron",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate3",
                        "type": "panel",
                        "label": "Smartschool",
                        "input": false,
                        "tableView": false,
                        "components": [
                            {
                                "html": "<p>Check https://crontab.guru/ for the layout of the cron template</p><p>To execute immediately, fill in 'now'</p>",
                                "label": "Content",
                                "refreshOnChange": false,
                                "key": "content",
                                "type": "content",
                                "input": false,
                                "tableView": false
                            },
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
                                "label": "Cron template",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "cron-scheduler-template",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "FROM Smartschool: update teachers (full name, ss username, ad username, ss internal number)",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "smartschool-update-teachers",
                                "type": "checkbox",
                                "input": true
                            },
                            {
                                "label": "FROM Smartschool: update students (full name, ss username, ad username, ss internal number)",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "smartschool-update-students",
                                "type": "checkbox",
                                "input": true
                            },
                            {
                                "label": "FROM Cardpresso: update students (RFID code)",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "cardpresso-update-students",
                                "type": "checkbox",
                                "input": true
                            },
                            {
                                "label": "TO AD: update accounts",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "ad-update-accounts",
                                "type": "checkbox",
                                "input": true
                            },
                            {
                                "label": "TO Papercut: update accounts",
                                "tableView": false,
                                "defaultValue": false,
                                "key": "papercut-update-accounts",
                                "type": "checkbox",
                                "input": true
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Smartschool",
                "tableView": false,
                "key": "smartschool",
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
                                "label": "Teacher groupname",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-teacher-group",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "WebAPI URL",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-api-url",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "WebAPI Key",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "smartschool-api-key",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Cardpresso",
                "tableView": false,
                "key": "cardpresso",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Cardpresso",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate2",
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
                                "label": "URL to server",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "cardpresso-url",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "Server login",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "cardpresso-login",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "Server password",
                                "labelPosition": "left-left",
                                "spellcheck": false,
                                "tableView": true,
                                "persistent": false,
                                "key": "cardpresso-password",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "Excel file location (use / or \\\\)",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "cardpresso-file",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Active Directory",
                "tableView": false,
                "key": "activeDirectory",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Active Directory",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate4",
                        "type": "panel",
                        "label": "Cardpresso",
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
                                "label": "URL to server",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "ad-url",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "Server login",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "ad-login",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            },
                            {
                                "label": "Server password",
                                "labelPosition": "left-left",
                                "spellcheck": false,
                                "tableView": true,
                                "persistent": false,
                                "key": "ad-password",
                                "type": "textfield",
                                "input": true,
                                "labelWidth": 20
                            }
                        ],
                        "collapsed": true
                    }
                ]
            },
            {
                "label": "Papercut",
                "tableView": false,
                "key": "papercut",
                "type": "container",
                "input": true,
                "components": [
                    {
                        "title": "Papercut",
                        "theme": "primary",
                        "collapsible": true,
                        "key": "RegistratieTemplate6",
                        "type": "panel",
                        "label": "Active Directory",
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
                                "label": "Server",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "papercut-server-url",
                                "type": "textfield",
                                "labelWidth": 20,
                                "input": true
                            },
                            {
                                "label": "Server port",
                                "labelPosition": "left-left",
                                "tableView": true,
                                "persistent": false,
                                "key": "papercut-server-port",
                                "type": "textfield",
                                "labelWidth": 20,
                                "input": true
                            },
                            {
                                "label": "Server authentication token",
                                "labelPosition": "left-left",
                                "spellcheck": false,
                                "tableView": true,
                                "persistent": false,
                                "key": "papercut-auth-token",
                                "type": "textfield",
                                "labelWidth": 20,
                                "input": true
                            }
                        ],
                        "collapsed": true
                    }
                ]
            }
        ]
    }