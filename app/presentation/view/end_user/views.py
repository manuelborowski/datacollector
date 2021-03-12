from flask import render_template, request, redirect
from . import end_user
from app import log, socketio, flask_app
import json, re
from app.presentation.view import prepare_registration_form
from app.application import register as mregister


@end_user.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if 'version' in request.args:
            profile = json.loads(request.args['profile'])
            data = {
                'student_first_name': profile['name'],
                'student_last_name': profile['surname'],
                'parent_first_name': profile['actualUserName'],
                'parent_last_name': profile['actualUserSurname'],
                'nbr_coaccount': profile['nrCoAccount'],
                'id': profile['internalnumber'],
            }
            ret = prepare_registration_form(data)
            if ret.code == ret.Result.E_ERROR:
                return render_template('end_user/messages.html', type='error')
            return render_template('end_user/register.html', data=ret.result,
                                   registration_endpoint = 'end_user.register_save')
        else:
            redirect_uri = f'{flask_app.config["SMARTSCHOOL_OUATH_REDIRECT_URI"]}/register'
            return redirect(f'{flask_app.config["SMARTSCHOOL_OAUTH_SERVER"]}?app_uri={redirect_uri}')
    except Exception as e:
        log.error(f'could not register {request.args}: {e}')
        return render_template('end_user/messages.html', type='error', info=e)


@end_user.route('/register_save', methods=['POST', 'GET'])
def register_save():
    try:
        data = json.loads(request.args['form_data'])
        ret = mregister.add_or_update_registration(data)
        if ret.code == ret.Result.E_ERROR:
           return render_template('end_user/messages.html', type='error')
        if ret.code == ret.Result.E_COULD_NOT_REGISTER:
            return render_template('end_user/messages.html', type='could-not-register')
        if ret.code == ret.Result.E_OK:
            return render_template('end_user/messages.html', type='ok', info=ret.result['timeslot'])
    except Exception as e:
        return render_template('end_user/messages.html', type='error', info=e)


