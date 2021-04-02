from . import person
from app import admin_required, log, supervisor_required
from flask import redirect, url_for, request, render_template
from flask_login import login_required
from app.presentation.view import base_multiple_items
from app.data import person as mdperson
from app.data.models import Person
from app.presentation.layout.utils import flash_plus, button_pressed
import json


@person.route('/person/show', methods=['POST', 'GET'])
@login_required
@supervisor_required
def show():
    return base_multiple_items.show(table_configuration)


@person.route('/person/table_ajax', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_ajax():
    return base_multiple_items.ajax(table_configuration)


@person.route('/person/table_action', methods=['GET', 'POST'])
@login_required
@supervisor_required
def table_action():
    pass


#     if button_pressed('edit'):
#         return item_edit()
#     if button_pressed('delete'):
#         return item_delete()
#
#
# def item_edit(done=False, id=-1):
#     try:
#         chbx_id_list = request.form.getlist('chbx')
#         if chbx_id_list:
#             id = int(chbx_id_list[0])  # only the first one can be edited
#         ret = prepare_registration_form(id=id)
#         if ret.result == ret.Result.E_COULD_NOT_REGISTER:
#             flash_plus('Fout opgetreden')
#         if ret.result == ret.Result.E_NO_REGISTRATION_FOUND:
#             flash_plus('Geen registratie gevonden')
#         return render_template('end_user/register.html', config_data=ret.registration,
#                                registration_endpoint = 'person.person_save')
#     except Exception as e:
#         log.error(f'could not edit person {request.args}: {e}')
#         return redirect(url_for('person.show'))
#
#
# def item_delete():
#     try:
#         chbx_id_list = request.form.getlist('chbx')
#         mperson.delete_registration(visit_id_list=chbx_id_list)
#     except Exception as e:
#         log.error(f'Could not delete registration: {e}')
#         flash_plus(u'Kan de registraties niet verwijderen', e)
#     return redirect(url_for('person.show'))
#
#
# @person.route('/person_save/<string:form_data>', methods=['POST', 'GET'])
# @login_required
# @supervisor_required
# def person_save(form_data):
#     try:
#         data = json.loads(form_data)
#         if data['cancel-person']:
#             try:
#                 mperson.delete_registration(code=data['registration-code'])
#             except Exception as e:
#                 flash_plus('Kon de reservatie niet verwijderen', e)
#         else:
#             try:
#                 ret = mperson.add_or_update_registration(data, update_by_end_user=False)
#                 if ret.result == ret.Result.E_NO_VISIT_SELECTED:
#                     flash_plus('Geen tijdslot geselecteerd')
#                 if ret.result == ret.Result.E_NOT_ENOUGH_VISITS:
#                     flash_plus('Niet genoeg tijdsloten')
#             except Exception as e:
#                 flash_plus('Onbekende fout opgetreden', e)
#     except Exception as e:
#         flash_plus('Onbekende fout opgetreden', e)
#     return redirect(url_for('person.show'))
#
#
# def update_meeting_cb(msg, client_sid=None):
#     if msg['data']['column'] == 8: # registration ack mail sent column
#         mperson.update_visit_email_sent_by_id(msg['data']['id'], msg['data']['value'])
#     if msg['data']['column'] == 9: # survey email sent column
#         mperson.update_visit_survey_email_sent_by_id(msg['data']['id'], msg['data']['value'])
#     if msg['data']['column'] == 10: # enable  column
#         mperson.update_visit_enable_by_id(msg['data']['id'], msg['data']['value'])
#     if msg['data']['column'] == 11:  # update tx-retry column
#         mperson.update_email_send_retry_by_id(msg['data']['id'], msg['data']['value'])
#     msocketio.send_to_room({'type': 'celledit-person', 'data': {'status': True}}, client_sid)
#
# msocketio.subscribe_on_type('celledit-person', update_meeting_cb)


# def ack_email_sent_cb(value, opaque):
#     msocketio.broadcast_message({'type': 'celledit-person', 'data': {'reload-table': True}})
#
#
# mperson.subscribe_visit_ack_email_sent(ack_email_sent_cb, None)
# mperson.subscribe_visit_survey_email_sent(ack_email_sent_cb, None)
# mperson.subscribe_visit_email_send_retry(ack_email_sent_cb, None)
# mperson.subscribe_visit_enabled(ack_email_sent_cb, None)
#
#
#
from app.presentation.view import false, true, null

filter_formio = \
    {
        "display": "form",
        "components": [
            {
                "label": "Columns",
                "columns": [
                    {
                        "components": [
                            {
                                "label": "Role",
                                "tableView": true,
                                "defaultValue": "teacher",
                                "data": {
                                    "values": [
                                        {
                                            "label": "All",
                                            "value": "all"
                                        },
                                        {
                                            "label": "Teacher",
                                            "value": "teacher"
                                        },
                                        {
                                            "label": "Student",
                                            "value": "student"
                                        }
                                    ]
                                },
                                "selectThreshold": 0.3,
                                "validate": {
                                    "onlyAvailableItems": false
                                },
                                "key": "filter-select-role",
                                "type": "select",
                                "indexeddb": {
                                    "filter": {}
                                },
                                "input": true,
                                "hideOnChildrenHidden": false
                            }
                        ],
                        "width": 6,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md"
                    },
                    {
                        "components": [
                            {
                                "label": "State",
                                "tableView": true,
                                "defaultValue": "all",
                                "data": {
                                    "values": [
                                        {
                                            "label": "All",
                                            "value": "all"
                                        },
                                        {
                                            "label": "New",
                                            "value": "new"
                                        },
                                        {
                                            "label": "Updated",
                                            "value": "updated"
                                        }
                                    ]
                                },
                                "selectThreshold": 0.3,
                                "validate": {
                                    "onlyAvailableItems": false
                                },
                                "key": "filter-select-state",
                                "type": "select",
                                "indexeddb": {
                                    "filter": {}
                                },
                                "input": true,
                                "hideOnChildrenHidden": false
                            }
                        ],
                        "width": 6,
                        "offset": 0,
                        "push": 0,
                        "pull": 0,
                        "size": "md"
                    }
                ],
                "key": "columns",
                "type": "columns",
                "input": false,
                "tableView": false
            }
        ]
    }

table_configuration = {
    'view': 'person',
    'title': 'Persons',
    'buttons': [],
    'delete_message': u'Do you want to remove this/these person(s)?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},

        {'name': 'Name', 'data': 'name', 'order_by': Person.full_name, 'orderable': True},
        {'name': 'AD username', 'data': 'ad_user_name', 'order_by': Person.ad_user_name, 'orderable': True},
        {'name': 'SS username', 'data': 'ss_user_name', 'order_by': Person.ss_user_name, 'orderable': True},
        {'name': 'SS intern', 'data': 'ss_internal_nbr', 'order_by': Person.ss_internal_nbr, 'orderable': True},
        {'name': 'RFID', 'data': 'rfid', 'order_by': Person.rfid_code, 'orderable': True},
        {'name': 'Role', 'data': 'role', 'order_by': lambda x: x['role'], 'orderable': True},
        {'name': 'N', 'data': 'new', 'order_by': lambda x: x['new'], 'orderable': True},
        {'name': 'U', 'data': 'updated', 'order_by': lambda x: x['updated'], 'orderable': True},
    ],
    'item': {
        # 'edit': {'title': 'Wijzig een reservatie', 'buttons': ['save', 'cancel']},
        # 'view': {'title': 'Bekijk een reservatie', 'buttons': ['edit', 'cancel']},
        # 'add': {'title': 'Voeg een reservatie toe', 'buttons': ['save', 'cancel']},
    },
    'href': [],
    'pre_filter': mdperson.pre_filter,
    'query_filter': mdperson.query_filter,
    'search_data': mdperson.search_data,
    'format_data': mdperson.format_data,
    'default_order': (1, 'asc'),
    'filterio': filter_formio,
    # 'socketio_endpoint': 'celledit-person',
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}

