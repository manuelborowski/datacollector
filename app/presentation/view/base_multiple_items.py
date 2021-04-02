from app.presentation.layout.utils import flash_plus, format_datatable
from app.application.multiple_items import prepare_data_for_ajax
from app.application import tables
from flask import render_template, get_flashed_messages, jsonify


def ajax(table_configuration):
    try:
        output = prepare_data_for_ajax(table_configuration)
        fml = get_flashed_messages()
        if not not fml:
            output['flash'] = fml
    except Exception as e:
        flash_plus(f'Table cannot be displayed (ajax)', e)
        output = []
    return jsonify(output)


def show(table_configuration):
    filters = []
    config = None
    try:
        config = tables.prepare_config_table_for_view(table_configuration)
    except Exception as e:
        flash_plus(f'Table cannot be displayed (show)', e)
    return render_template('base_multiple_items.html', table_config=config, filters=filters)
