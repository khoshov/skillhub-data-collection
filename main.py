
import os

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler
from pytz import timezone

from otzovik_feedbacks_parser.otzovik_selenium_parser import run_otzovik_update_data_job
from irecommend_feedbacks_parser.irecommend_selenium_parser import run_irecommend_update_data_job
from mooc_feedbacks_parser.mooc_requests_parser import run_mooc_parser


def listener(event):
    if not event.exception:
        job = scheduler.get_job(event.job_id)
        print(f"задания в работе {job}")
        print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))


if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.configure(timezone=timezone('Europe/Moscow'))
    scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    # запуск парсера отзовик через Selenium
    # каждый день в 3 часа ночи
    scheduler.add_job(
        run_otzovik_update_data_job,
        'cron',
        hour='3',
        minute='00',
        id="otzovik_parser")
    # запуск irecomend через Selenium
    # каждый день в 1 час ночи
    scheduler.add_job(
        run_irecommend_update_data_job,
        'cron',
        hour='1',
        minute='00',
        id="irecomend_parser")
    # запуск парсера mooc через requests
    # каждый день в 00 час 10 минут ночи
    scheduler.add_job(
        run_mooc_parser,
        'cron',
        hour='0',
        minute='10',
        id="irecomend_parser")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
