from app import flask_app, log
import datetime

def execute_test(args):
    try:
        test_code = flask_app.config['ENTER_TEST_CODE']
        if 'help' in args:
            return '''
            enter?code=umagbinnen : test gebruiker, gebruik test delay settings<br>
            enter?code=droogloop : test gebruiker, gebruik guest delay settings<br>
            test?umagbinnen=delay: test gebruiker (umagbinnen), timeslot wordt gezet op NU + delay<br> 
            '''
        if test_code in args:
            pass
            return f'test ({test_code})'
    except Exception as e:
        log.error(f'test: could not do test {args}: {e}')
    return f'sorry, niet gelukt'