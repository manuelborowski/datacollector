from app.data import settings as msettings
from app import log, message_scheduler, flask_app, soap
import datetime, time

def send_message(to_id, to_nbr_coaacount, subject, content):
    try:
        from_id = flask_app.config['SMARTSCHOOL_SEND_FROM']
        api_key = flask_app.config['SMARTSCHOOL_API_KEY']

        ret = soap.service.sendMsg(api_key, to_id, subject, content, from_id, '', to_nbr_coaacount, 0)
        if ret == 0:
            return True
        else:
            log.error(f'send_message: ERROR, could not send message, returned: {ret}')
    except Exception as e:
        log.error(f'send_message: ERROR, could not send message: {e}')
    return False


send_message_config = []

def subscribe_send_message(cb, args):
    if cb:
        send_message_config.append({
            'function': cb,
            'args': args
        })


run_message_task = True
def send_message_task():
    nbr_sent_per_minute = 0
    while run_message_task:
        with flask_app.app_context():
            at_least_one_message_sent = True
            start_time = datetime.datetime.now()
            job_interval = msettings.get_configuration_setting('message-task-interval')
            messages_per_minute = msettings.get_configuration_setting('message-per-minute')
            while at_least_one_message_sent:
                at_least_one_message_sent = False
                for send_message in send_message_config:
                    if run_message_task and msettings.get_configuration_setting('enable-send-message'):
                        ret = send_message['function'](**send_message['args'])
                        if ret:
                            nbr_sent_per_minute += 1
                            now = datetime.datetime.now()
                            delta = now - start_time
                            if (nbr_sent_per_minute >= messages_per_minute) and (delta < datetime.timedelta(seconds=60)):
                                time_to_wait = 60 - delta.seconds + 1
                                log.info(f'send_message_task: have to wait for {time_to_wait} seconds')
                                time.sleep(time_to_wait)
                                nbr_sent_per_minute = 0
                                start_time = datetime.datetime.now()
                            at_least_one_message_sent = True
        if run_message_task:
                now = datetime.datetime.now()
                delta = now - start_time
                if delta < datetime.timedelta(seconds=job_interval):
                    time_to_wait = job_interval - delta.seconds
                    time.sleep(time_to_wait)


def set_base_url(url):
    msettings.set_configuration_setting('base-url', url)


def stop_send_message_task():
    global run_message_task
    run_message_task = False


def start_send_message_task():
    running_job = message_scheduler.get_job('send_message_task')
    if running_job:
        message_scheduler.remove_job('send_message_task')
    message_scheduler.add_job('send_message_task', send_message_task)

start_send_message_task()

