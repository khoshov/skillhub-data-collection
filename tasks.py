from celery import Celery
from celery.schedules import crontab

from settings.urls_config import TUTORTOP_MAIN_PAGE
from tutortop_parser.tutortop_parser import load_main_page_course_links, load_courses_data_by_category_url


celery_app = Celery('tasks', broker='redis://localhost:6379/0')

celery_app.conf.timezone = 'Europe/Moscow'

@celery_app.task
def run_tutortop_parser():
    courses_category_links = load_main_page_course_links(TUTORTOP_MAIN_PAGE)
    for category, url in courses_category_links.items():
        load_courses_data_by_category_url(url, category)


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(minute=0, hour=5, day_of_week=1), run_tutortop_parser.s())
    sender.add_periodic_task(crontab(minute='*/5'), run_tutortop_parser.s())
