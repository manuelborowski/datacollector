from app import log, flask_app, CronTaskSequence
from app.data import person as mperson
from app.data.models import Person
from app.application import settings as msettings, cron as mcron
import datetime, os, filecmp, shutil, pyexcel
from zeep import Client
import json, paramiko
from paramiko import sftp_client
from pathlib import Path

CARDPRESSO_TASK = 'cardpresso-task'
CARDPRESSO_LOCATION = f'{os.getcwd()}/app{flask_app.static_url_path}/cardpresso'

client = paramiko.SSHClient()
home = str(Path.home())
client.load_host_keys(f'{home}/.ssh/known_hosts')

HEADING_NAME = 'NAAM'
HEADING_FIRST_NAME = 'VOORNAAM'
HEADING_STUDENT_ID = 'LEERLINGNUMMER'
HEADING_BADGE = 'RFID'
HEADING_USER_ID = 'GEBRUIKERSNAAMSORT'


def read_from_cardpresso_database(update_students=False, force_update=False):
    try:
        if update_students:
            username = msettings.get_configuration_setting('cardpresso-login')
            password = msettings.get_configuration_setting('cardpresso-password')
            url = msettings.get_configuration_setting('cardpresso-url')
            remote_file = msettings.get_configuration_setting('cardpresso-file').replace('\\\\', '/')
            filename = Path(remote_file).name
            local_file = f'{CARDPRESSO_LOCATION}/{filename}'
            if force_update:
                os.remove(local_file)
            local_temp_file = f'{CARDPRESSO_LOCATION}/temp.xlsm'
            client.connect(url, username=username, password=password)
            transport = client.get_transport()
            sftp = sftp_client.SFTPClient.from_transport(transport)
            sftp.get(remote_file, local_temp_file)
            sftp.close()
            try:
                file_updated = not filecmp.cmp(local_file, local_temp_file)
            except FileNotFoundError:
                file_updated = True
            if file_updated:
                students = mperson.get_persons(role=mperson.ROLE.STUDENT)
                students_cache = {s.ss_internal_nbr: s for s in students}
                lines = pyexcel.iget_records(file_name=local_temp_file)
                nbr_updated_students = 0
                for line in lines:
                    if str(line[HEADING_STUDENT_ID]) in students_cache:
                        student = students_cache[str(line[HEADING_STUDENT_ID])]
                        if student.rfid_code != line[HEADING_BADGE]:
                            student.rfid_code = line[HEADING_BADGE]
                            mperson.update_flag(student, True)
                            nbr_updated_students += 1
                mperson.end_update_bulk_person()
                log.info(f'update from cardpresso database students: updated: {nbr_updated_students}/')
                shutil.copyfile(local_temp_file, local_file)
    except Exception as e:
        log.eror(f'update from cardpresso database error: {e}')


def cardpresso_cront_task(opaque):
    update_students = msettings.get_configuration_setting('cardpresso-update-students')
    with flask_app.app_context():
        read_from_cardpresso_database(update_students)


mcron.subscribe_cron_task(CronTaskSequence.CARDPRESSO, cardpresso_cront_task, None)
