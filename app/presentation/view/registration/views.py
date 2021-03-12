from flask import request, redirect, url_for
from flask_login import login_required, current_user
from app.data.registration import format_data, pre_filter
from app import db, log, admin_required, data
from . import registration
from app.presentation.view import base_multiple_items
from app.data.models import Registration, Timeslot
from app.presentation.layout.utils import flash_plus, button_pressed
from app.application import register as mregister

@registration.route('/registration', methods=['GET', 'POST'])
@login_required
def show():
    if current_user.is_strict_user:
        configuration['buttons'] = []
    else:
        configuration['buttons'] = ['delete']

    return base_multiple_items.show(configuration)


@registration.route('/registration/table_ajax', methods=['GET', 'POST'])
@login_required
def table_ajax():
    return base_multiple_items.ajax(configuration)


@registration.route('/registration/table_action', methods=['GET', 'POST'])
@login_required
def table_action():
    if button_pressed('delete'):
        return item_delete()


@registration.route('/registration/item_action/<string:action>', methods=['GET', 'POST'])
@login_required
def item_action(action=None):
    pass


def item_delete():
    try:
        chbx_id_list = request.form.getlist('chbx')
        mregister.delete_registration(chbx_id_list)
    except Exception as e:
        log.error(u'Could not delete registration: {}'.format(e))
        flash_plus('Could not delete registration', e)
    return redirect(url_for('registration.show'))


configuration = {
    'view': 'registration',
    'title': 'Registraties',
    'buttons': ['delete'],
    'delete_message': u'Bent u zeker dat u deze registratie(s) wilt verwijderen?',
    'template': [
        {'name': 'row_action', 'data': 'row_action', 'width': '2%'},
        {'name': 'Tijdslot', 'data': 'timeslot-date', 'order_by': Timeslot.date, 'orderable': True, 'width': '15%'},
        {'name': 'Leerling', 'data': 'student_name', 'width': '15%'},
        {'name': 'Ouder', 'data': 'parent_name', 'width': '15%'},
        {'name': 'Meeting', 'data': 'timeslot-meeting-url'},
        ],
    'filter': [],
    'item': {},
    'href': [],
    'pre_filter': pre_filter,
    'format_data': format_data,
    'default_order': (1, 'asc'),
    # 'cell_color': {'supress_cell_content': True, 'color_keys': {'X': 'red', 'O': 'green'}}, #TEST
    # 'suppress_dom': True,

}
