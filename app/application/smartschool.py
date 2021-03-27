from app import log, flask_app, CronTaskSequence
from app.data import person as mperson
from app.data.models import Person
from app.application import settings as msettings, cron as mcron
import datetime
from zeep import Client
import json, re

# TEACHERS_GROUP = 'leerkracht'
TEACHERS_GROUP = 'Klassenraad 3A'

# STUDENTS_GROUP = 'leerlingen'
STUDENTS_GROUP = '3ORb (1 en 2)'

# leerkracht 0
# leerling 1
# andere 13
# directie 30

def update_smartschool(opaque):
    with flask_app.app_context():
        try:
            api_key = msettings.get_configuration_setting('smartschool-api-key')
            api_url = msettings.get_configuration_setting('smartschool-api-url')
            soap = Client(api_url)
            update_teachers = msettings.get_configuration_setting('smartschool-update-teachers')
            update_students = msettings.get_configuration_setting('smartschool-update-students')

            # if update_teachers:
            #     current_teachers = mperson.get_persons(role=mperson.ROLE.TEACHER)
            #     current_teacher_user_names = {}
            #     for teacher in current_teachers:
            #         current_teacher_user_names[teacher.ss_user_name] = teacher
            #         mperson.activate_person(teacher, False)
            #     ret = soap.service.getAllAccountsExtended(api_key, TEACHERS_GROUP, 1)
            #     if not isinstance(ret, int):
            #         new_teachers = json.loads(ret)
            #         nbr_new_teachers = 0
            #         nbr_udpated_teachers = 0
            #         for new_teacher in new_teachers:
            #             ss_user_name = new_teacher['gebruikersnaam']
            #             if ss_user_name in current_teacher_user_names:
            #                 current_teacher = current_teacher_user_names[ss_user_name]
            #                 full_name = f'{new_teacher["voornaam"]} {new_teacher["naam"]}'
            #                 if current_teacher.full_name != full_name \
            #                         or current_teacher.ss_internal_nbr != new_teacher['internnummer']:
            #                     mperson.update_bulk_person(current_teacher, full_name=full_name,
            #                                           ss_internal_nbr=new_teacher['internnummer'], active=True)
            #                     nbr_udpated_teachers += 1
            #                 else:
            #                     mperson.activate_person(current_teacher, True)
            #             else:
            #                 mperson.add_bulk_person(full_name=f'{new_teacher["voornaam"]} {new_teacher["naam"]}',
            #                                         ss_user_name=ss_user_name,
            #                                         ss_internal_nbr=new_teacher['internnummer'],
            #                                         ad_user_name=ss_user_name, role=mperson.ROLE.TEACHER)
            #                 nbr_new_teachers += 1
            #         log.info(f'new/updated teachers: {nbr_new_teachers}/{nbr_udpated_teachers}')
            #         mperson.end_add_bulk_person()
            #     else:
            #         error_codes = soap.service.returnJsonErrorCodes()
            #         error = error_codes[str(ret)]
            #         log.eror(f'updating smartschool teachers: soap returned: {error}')

            if update_teachers:
                current_teachers = mperson.get_persons(role=mperson.ROLE.TEACHER)
                current_teacher_user_names = {}
                nbr_active_teachers_before = mperson.get_person_count(active=True, role=mperson.ROLE.TEACHER)
                for teacher in current_teachers:
                    current_teacher_user_names[teacher.ss_user_name] = teacher
                    mperson.activate_person(teacher, False)
                ret = soap.service.getAllAccountsExtended(api_key, TEACHERS_GROUP, 1)
                if not isinstance(ret, int):
                    new_teachers = json.loads(ret)
                    nbr_new_teachers = 0
                    for new_teacher in new_teachers:
                        ss_user_name = new_teacher['gebruikersnaam']
                        if ss_user_name in current_teacher_user_names:
                            current_teacher = current_teacher_user_names[ss_user_name]
                            full_name = f'{new_teacher["voornaam"]} {new_teacher["naam"]}'
                            if current_teacher.full_name != full_name:
                                current_teacher.full_name = full_name
                                mperson.update_flag(current_teacher, True)
                            if current_teacher.ss_internal_nbr != new_teacher['internnummer']:
                                current_teacher.ss_internal_nbr = new_teacher['internnummer']
                                mperson.update_flag(current_teacher, True)
                            mperson.activate_person(current_teacher, True)
                        else:
                            mperson.add_bulk_person(full_name=f'{new_teacher["voornaam"]} {new_teacher["naam"]}',
                                                    ss_user_name=ss_user_name,
                                                    ss_internal_nbr=new_teacher['internnummer'],
                                                    ad_user_name=ss_user_name, role=mperson.ROLE.TEACHER)
                            nbr_new_teachers += 1
                    mperson.end_add_bulk_person()
                    nbr_active_teachers_after = mperson.get_person_count(active=True, role=mperson.ROLE.TEACHER)
                    nbr_updated_teachers = mperson.get_person_count(updated=True, role=mperson.ROLE.TEACHER)
                    log.info(f'smartschool teachers: new/updated/active-before/active-after: {nbr_new_teachers}/' \
                            f'{nbr_updated_teachers}/{nbr_active_teachers_before}/{nbr_active_teachers_after}')
                else:
                    error_codes = soap.service.returnJsonErrorCodes()
                    error = error_codes[str(ret)]
                    log.eror(f'updating smartschool teachers: soap returned: {error}')

            if update_students:
                current_students = mperson.get_persons(role=mperson.ROLE.STUDENT)
                current_student_user_names = {}
                nbr_active_students_before = mperson.get_person_count(active=True, role=mperson.ROLE.STUDENT)
                for student in current_students:
                    current_student_user_names[student.ss_user_name] = student
                    mperson.activate_person(student, False)
                ret = soap.service.getAllAccountsExtended(api_key, STUDENTS_GROUP, 1)
                if not isinstance(ret, int):
                    new_students = json.loads(ret)
                    nbr_new_students = 0
                    for new_student in new_students:
                        if new_student['basisrol'] != '1': continue
                        ss_user_name = new_student['gebruikersnaam']
                        if ss_user_name in current_student_user_names:
                            current_student = current_student_user_names[ss_user_name]
                            full_name = f'{new_student["voornaam"]} {new_student["naam"]}'
                            if current_student.full_name != full_name:
                                current_student.full_name = full_name
                                mperson.update_flag(current_student, True)
                            if current_student.ss_internal_nbr != new_student['internnummer']:
                                current_student.ss_internal_nbr = new_student['internnummer']
                                mperson.update_flag(current_student, True)
                            mperson.activate_person(current_student, True)
                        else:
                            ad_user_name = ss_user_name
                            ad_user_name = re.sub("[ùÜü]", "u", ad_user_name)
                            ad_user_name = re.sub("[ ]", "", ad_user_name)
                            ad_user_name = re.sub("[Öö]", "o", ad_user_name)
                            ad_user_name = re.sub("[ç]", "c", ad_user_name)
                            ad_user_name = re.sub("[ï]", "i", ad_user_name)
                            ad_user_name = re.sub("[.]", "", ad_user_name)
                            ad_user_name = re.sub("[ãÃ]", "a", ad_user_name)
                            ad_user_name = re.sub("[Ğğ]", "g", ad_user_name)
                            ad_user_name = re.sub("[ËÉÈ_Êëéèê]", "e", ad_user_name)
                            ad_user_name = re.sub("[şŞ]", "s", ad_user_name)
                            mperson.add_bulk_person(full_name=f'{new_student["voornaam"]} {new_student["naam"]}',
                                                    ss_user_name=ss_user_name,
                                                    ss_internal_nbr=new_student['internnummer'],
                                                    ad_user_name=ad_user_name, role=mperson.ROLE.STUDENT)
                            nbr_new_students += 1
                    mperson.end_add_bulk_person()
                    nbr_active_students_after = mperson.get_person_count(active=True, role=mperson.ROLE.STUDENT)
                    nbr_updated_students = mperson.get_person_count(updated=True, role=mperson.ROLE.STUDENT)
                    log.info(f'smartschool students: new/updated/active-before/active-after: {nbr_new_students}/' \
                            f'{nbr_updated_students}/{nbr_active_students_before}/{nbr_active_students_after}')
                else:
                    error_codes = soap.service.returnJsonErrorCodes()
                    error = error_codes[str(ret)]
                    log.eror(f'updating smartschool students: soap returned: {error}')

        except Exception as e:
            log.eror(f'smartschool job task: {e}')


mcron.subscribe_cron_task(CronTaskSequence.SMARTSCHOOL, update_smartschool, None)


