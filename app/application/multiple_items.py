from flask import request
from sqlalchemy import or_, func
import time, datetime, json

from app import data

from app import log, db, data
from app.application import tables


######################################################################################################
###                                       Build a generic filter
######################################################################################################

def check_date_in_form(date_key, form):
    if date_key in form and form[date_key] != '':
        try:
            time.strptime(form[date_key].strip(), '%d-%M-%Y')
            return form[date_key].strip()
        except Exception as e:
            data.utils.raise_error('Verkeerd datumformaat, moet in de vorm zijn: d-m-y', e)
    return ''


def check_value_in_form(value_key, form):
    if value_key in form and form[value_key] != '':
        try:
            float(form[value_key])
            return form[value_key]
        except Exception as e:
            data.utils.raise_error('Verkeerde getal notatie', e)
    return ''


def check_string_in_form(value_key, form):
    if value_key in form and form[value_key] != '':
        try:
            str(form[value_key])
            return form[value_key]
        except Exception as e:
            data.utils.raise_error('Verkeerde tekst notatie', e)
    return ''


def prepare_data_for_ajax(table_configuration, paginate=True):
    try:
        data_table = json.loads(request.form['data_table'])
        template = table_configuration['template']
        # a composed query is a tree like query, i.e. the roots are retrieved via an explicit SQL query and the attached
        # leaves are implicitly retrieved and put in a tree like ORM structure
        composed_query = table_configuration['composed_query'] if 'composed_query' in table_configuration else None

        if 'pre_filter' in table_configuration:
            sql_query = table_configuration['pre_filter']()

            total_count = sql_query.count()

            if 'query_filter' in table_configuration:
                sql_query = table_configuration['query_filter'](sql_query, data_table['filter'])

            # search, if required
            search_value = data_table['search']['value'] if 'search' in data_table else None
            if search_value:
                a = search_value.split('-')[::-1]
                a[0] += '%'
                search_date = '%' + '-'.join(a) + '%'
                search_value = '%' + search_value + '%'
                search_constraints = []
                if 'search_data' in table_configuration:
                    search_constraints = table_configuration['search_data'](search_value)
                if search_constraints:
                    sql_query = sql_query.filter(or_(*search_constraints))

            filtered_count = sql_query.count()

            order_column = data_table['order'][0]['column']
            order_dir = data_table['order'][0]['dir']
            order_by = template[order_column]['order_by']
            order_table_in_sql = not callable(order_by)
            if 'row_detail' in table_configuration:
                order_column -= 1

            paginate_start = paginate_length = None
            if paginate:
                paginate_start = data_table['start']
                paginate_length = data_table['length']

            if order_table_in_sql:
                # order the table via the SQL query based on a specified table-column
                if isinstance(order_by, list):
                    for i in order_by:
                        sql_query = sql_query.order_by(i.desc()) if order_dir == 'desc' else sql_query.order_by(i)
                else:
                    sql_query = sql_query.order_by(order_by.desc()) if order_dir == 'desc' else sql_query.order_by(order_by)
                # if it is a composed query, execute the composed query
                # else if it is a flat query, paginate in SQL and do SQL query
                if composed_query:
                    stripped_search_value = search_value[1:-1] if search_value else None
                    filtered_list, total_count, filtered_count = composed_query(sql_query.all(),
                                                                                search_string=stripped_search_value)
                else:
                    if paginate_start:
                        sql_query = sql_query.slice(paginate_start, paginate_start + paginate_length)
                    filtered_list = sql_query.all()
                # format the list
                formatted_list = table_configuration['format_data'](filtered_list)
                # if it is a composed query, it is still required to paginate
                if composed_query and paginate_start:
                    formatted_list = formatted_list[paginate_start:paginate_start + paginate_length]
            else:
                # order the list based on a user specified lambda function
                # if it is a composed query, execute the composed query
                # else if it is a flat query, do the SQL query
                if composed_query:
                    stripped_search_value = search_value[1:-1] if search_value else None
                    filtered_list, total_count, filtered_count = composed_query(sql_query.all(),
                                                                                search_string=stripped_search_value)
                else:
                    filtered_list = sql_query.all()
                # format, order and and paginate
                formatted_list = table_configuration['format_data'](filtered_list)
                formatted_list = sorted(formatted_list, key=order_by, reverse=(order_dir == 'desc'))
                if paginate_start:
                    formatted_list = formatted_list[paginate_start:paginate_start + paginate_length]
        else:
            formatted_list = table_configuration['format_data']()
            total_count = filtered_count = len(formatted_list)

    except Exception as e:
        log.error(f'could not prepare data for ajax: {e}')
        data.utils.raise_error('prepare_data_for_ajax', e)
    output = {
        'draw': str(data_table['draw']),
        'recordsTotal': str(total_count),
        'recordsFiltered': str(filtered_count),
        'data': formatted_list}
    return output
