from app import log, flask_app, CronTaskSequence
from app.data import person as mperson
from app.data.models import Person
from app.application import settings as msettings, cron as mcron
import datetime, os, filecmp, shutil, pyexcel
from zeep import Client
import json, paramiko
import xmlrpc.client
from paramiko import sftp_client
from pathlib import Path

PAPERCUT_TASK = 'papercut-task'
PAPERCUT_LOCATION = f'{os.getcwd()}/app{flask_app.static_url_path}/papercut'

ssh_client = paramiko.SSHClient()
home = str(Path.home())
ssh_client.load_host_keys(f'{home}/.ssh/known_hosts')

HEADING_NAME = 'NAAM'
HEADING_FIRST_NAME = 'VOORNAAM'
HEADING_STUDENT_ID = 'LEERLINGNUMMER'
HEADING_BADGE = 'RFID'
HEADING_USER_ID = 'GEBRUIKERSNAAMSORT'

PROPERTY_RFID = 'primary-card-number'

def update_papercut(opaque):
    with flask_app.app_context():
        try:
            update_students = msettings.get_configuration_setting('papercut-update-students')
            if update_students:
                username = msettings.get_configuration_setting('papercut-login')
                password = msettings.get_configuration_setting('papercut-password')
                url = msettings.get_configuration_setting('papercut-url')
                remote_file = msettings.get_configuration_setting('papercut-file').replace('\\\\', '/')
                filename = Path(remote_file).name
                local_file = f'{PAPERCUT_LOCATION}/{filename}'
                local_temp_file = f'{PAPERCUT_LOCATION}/temp.xlsm'
                ssh_client.connect(url, username=username, password=password)
                transport = ssh_client.get_transport()
                sftp = sftp_client.SFTPClient.from_transport(transport)
                sftp.get(remote_file, local_temp_file)
                sftp.close()
                ssh_client.close()
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
                    log.info(f'papercut students: updated: {nbr_updated_students}/')
                    shutil.copyfile(local_temp_file, local_file)
        except Exception as e:
            log.error(f'papercut job task: {e}')


# mcron.subscribe_cron_task(CronTaskSequence.PAPERCUT, update_papercut, None)


def update_scripts_on_papercut_server(skip_ssh_connect=False):
    try:
        remote_script_path = msettings.get_configuration_setting('papercut-script-path').replace('\\\\', '/')
        scripts = msettings.get_configuration_setting('papercut-scripts')
        out = []
        script_name = None
        if not skip_ssh_connect:
            url = msettings.get_configuration_setting('papercut-url')
            login = msettings.get_configuration_setting('papercut-login')
            password = msettings.get_configuration_setting('papercut-password')
            ssh_client.connect(url, username=login, password=password)
        transport = ssh_client.get_transport()
        sftp = sftp_client.SFTPClient.from_transport(transport)
        for line in scripts.split('\n'):
            if 'SCRIPT-START' in line:
                script_name = line.strip().split(' ')[-1]
                out = []
            elif 'SCRIPT-STOP' in line:
                local_script_file = f'{PAPERCUT_LOCATION}/{script_name}'
                with open(local_script_file, "w") as f:
                    f.writelines(out)
                sftp.put(local_script_file, script_name)
            else:
                out.append(f'{line}\n')
        sftp.close()
        if not skip_ssh_connect:
            ssh_client.close()
    except Exception as e:
        log.error('Could not update papercut scripts: {e}')


def get_rfids():
    try:
        url = msettings.get_configuration_setting('papercut-server-url')
        port = msettings.get_configuration_setting('papercut-server-port')
        token = msettings.get_configuration_setting('papercut-auth-token')
        nbr_updated_rfid = 0
        nbr_user_not_found = 0
        with xmlrpc.client.ServerProxy(f'http://{url}:{port}/rpc/api/xmlrpc') as server:
            persons = mperson.get_persons(enabled=True, active=True)
            for person in persons:
                try:
                    property = server.api.getUserProperty(token, person.ad_user_name, PROPERTY_RFID)
                    if person.rfid_code != property:
                        person.rfid_code = property
                        nbr_updated_rfid += 1
                except Exception as e:
                    nbr_user_not_found += 1
                    log.info(f'get person rfid: person not found: {person.ad_user_name}, error: {e}')
        mperson.end_update_bulk_person()
        log.info(f'get rfids from papercut: nbr-persons/nbr-updated/nbr-not-found {len(persons)}/{nbr_updated_rfid}/{nbr_user_not_found}')
        return {'status': True, 'message': f'RFIDs from papercut\nnbr: {len(persons)}\nupdated {nbr_updated_rfid}\nnot found {nbr_user_not_found}'}
    except Exception as e:
        log.error('get rfids: error {e}')
        return {'status': False, 'message': f'{e}'}
