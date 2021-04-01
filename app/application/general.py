from app import log
from app.data import person as mperson
from app.application import smartschool as msmartschool, papercut as mpapercut, cardpresso as mcardpresso
from app.application import cron as mcron


def clear_database():
    try:
        persons = mperson.get_persons()
        mperson.delete_persons(persons=persons)
    except Exception as e:
        log.error(f'could not clear database: {e}')
        return {'status': False, 'message': str(e)}
    log.info('database is cleared')
    return {'status': True,'message': 'Database is cleared'}


def populate_database():
    try:
        msmartschool.read_from_smartschool_database(True, True)
        mpapercut.get_rfids()
        # mcardpresso.read_from_cardpresso_database(True, True)
        clear_update_and_new_flags()
    except Exception as e:
        log.error(f'could not populate database: {e}')
        return {'status': False, 'message': str(e)}
    log.info('database is populated')
    return {'status': True,'message': 'Database is populated'}


def clear_update_and_new_flags():
    try:
        persons = mperson.get_persons()
        for person in persons:
            mperson.update_flag(person, False)
            mperson.new_flag(person, False)
        mperson.end_update_bulk_person()
    except Exception as e:
        log.error(f'could not clear update and new flags:{e}')


def update_database_now():
    try:
        mcron.start_job_now()
    except Exception as e:
        log.error(f'could not execute database update:{e}')
        return {'status': False, 'message': str(e)}
    return {'status': True, 'message': 'Database update ongoing...'}
