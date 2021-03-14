from app import ap_scheduler, log, flask_app
from app.data import teacher as mteacher
from app.data.models import Teacher
from app.application import settings as msettings
import datetime
from apscheduler.triggers.cron import CronTrigger
from zeep import Client
import json

SMARTSCHOOL_TASK = 'smartschool-task'


def scheduler_task():
    with flask_app.app_context():
        try:
            print(datetime.datetime.now())
            current_teachers = mteacher.get_teachers()
            current_teacher_user_names = {}
            for teacher in current_teachers:
                current_teacher_user_names[teacher.user_name] = teacher
                teacher.enabled = False
            group = msettings.get_configuration_setting('smartschool-teacher-group')
            api_key = msettings.get_configuration_setting('smartschool-api-key')
            api_url = msettings.get_configuration_setting('smartschool-api-url')
            soap = Client(api_url)
            ret = soap.service.getAllAccountsExtended(api_key, group, 1)
            teachers = json.loads(ret)
            # with open('/home/aboro/projects/datacollector/smartschool.json', 'r', encoding='utf-8') as f:
            #     teachers = json.load(f)
            nbr_new_teachers = 0
            nbr_udpated_teachers = 0
            for teacher in teachers:
                user_name = teacher['gebruikersnaam']
                if user_name in current_teacher_user_names:
                    current_teacher = current_teacher_user_names[user_name]
                    current_teacher.full_name = f'{teacher["voornaam"]} {teacher["naam"]}'
                    current_teacher.smartschool_id = teacher['internnummer']
                    current_teacher.enabled = True
                    current_teacher.set_smartschool_flag(Teacher.SS_TEACHER_FLAG)
                    nbr_udpated_teachers += 1
                else:
                    mteacher.add_bulk_teacher(name=f'{teacher["voornaam"]} {teacher["naam"]}', user_name=user_name,
                                              smartschool_id=teacher['internnummer'], enabled=True,
                                              smartschool_flags=Teacher.SS_TEACHER_FLAG)
                    nbr_new_teachers += 1
            log.info(f'new/updated teachers: {nbr_new_teachers}/{nbr_udpated_teachers}')
            mteacher.end_add_bulk_teacher()
        except Exception as e:
            log.eror(f'smartschool job task: {e}')


def update_job(setting, value, opaque):
    try:
        if setting == 'smartschool-scheduler-cron':
            init_job(value)
    except Exception as e:
        log.error(f'could not update smartschool job: {e}')


def init_job(cron_template):
    try:
        running_job = ap_scheduler.get_job(SMARTSCHOOL_TASK)
        if running_job:
            ap_scheduler.remove_job(SMARTSCHOOL_TASK)
        if cron_template == 'now':
            ap_scheduler.add_job(SMARTSCHOOL_TASK, scheduler_task, next_run_time=datetime.datetime.now())
        else:
            ap_scheduler.add_job(SMARTSCHOOL_TASK, scheduler_task, trigger=CronTrigger.from_crontab(cron_template))
    except Exception as e:
        log.error(f'could not init smartschool job: {e}')


def start_job():
    try:
        cron_template = msettings.get_configuration_setting('smartschool-scheduler-cron')
        init_job(cron_template)
        msettings.subscribe_handle_update_setting('smartschool-scheduler-cron', update_job, None)
    except Exception as e:
        log.error(f'could not start smartschool job: {e}')


start_job()
