import csv
import re
from datetime import datetime
from time import sleep
from typing import Dict

from bs4 import BeautifulSoup

from base_func.http_requests import fetch_html, send_parse_data
from settings.logger_settings import logger
from settings.mapping import COURSE_DURATION_TYPE


@logger.catch
def load_main_page_course_links(home_page_url: str) -> Dict:
    """ фунция собирает ссылки на разделы с курсами с главной страницы """
    courses_links = {}
    houme_page_soup_data = BeautifulSoup(fetch_html(home_page_url).text, 'lxml')
    courses_catalog = houme_page_soup_data.select(".submenu__wrap__mark")[2].select("a")
    for item in courses_catalog[1:]:
        courses_links[item.get_text()] = item['href']
    return courses_links


@logger.catch
def load_courses_data_by_category_url(url: str, course_category: str) -> None:
    """ функция собирает дынные о платных и бесплатных курсах в категории """
    courses_page_soup_data = BeautifulSoup(fetch_html(url).text, 'lxml')
    fetch_all_paid_courses_data_by_category(courses_page_soup_data, course_category)
    fetch_all_free_courses_data_by_category(courses_page_soup_data, course_category)
    sleep(15)


@logger.catch
def fetch_all_paid_courses_data_by_category(courses_page_soup_data, course_category: str) -> None:
    """ функция собирает данные о платных курсах в категории """
    courses_table = courses_page_soup_data.select('.tab-course-paid .tab-course-item')
    for course_item in courses_table:
        course_data = {
            "school": course_item['data-school'],
            "course_category": course_category,
            "course_title": course_item.select_one('.m-course-title').get_text().strip(),
            "course_price": course_item['data-price'],
            "course_start_date": _render_course_start_date(course_item),
            "course_duration": float(course_item['data-dlitelnost']),
            "course_duration_type": COURSE_DURATION_TYPE['MONTH'],
            "course_link": _find_course_url(course_item),
        }
        send_parse_data(course_data)


@logger.catch
def fetch_all_free_courses_data_by_category(courses_page_soup_data, course_category: str) -> None:
    """ функция собирает данные о бесплатных курсах в категории """
    courses_table = courses_page_soup_data.select('.tab-free-course .tab-course-item')
    for course_item in courses_table:
        course_data = {
            "school": course_item['data-school'],
            "course_category": course_category,
            "course_title": course_item.select_one('.m-course-title').get_text().strip(),
            "course_price": None,
            "course_start_date": None,
            "course_duration": f"{course_item['data-dlitelnost']}",
            "course_duration_type": COURSE_DURATION_TYPE['LESSON'],
            "course_link": _find_course_url(course_item),
            "course_format": course_item.select_one('.tab-course-col-format_obucheniy').get_text().strip(),
        }
        send_parse_data(course_data)


@logger.catch
def _find_course_url(course_row_data: str) -> str:
    """ Функция поиска ссылки на курс из генератора аффилированной ссылки """
    course_referal_url = course_row_data.select_one('a.tab-link-course')['href']
    course_referal_url_generator = fetch_html(course_referal_url).text
    re_patterns = [r"\?dl=(.+?)(';|#|\?ref|&subid)", r"ulp=(.+)';", r"href\s=\s'(.+?)(\?unit|'|\?utm|\?ref)"]
    for pattern in re_patterns:
        if re.search(pattern, course_referal_url_generator):
            return re.search(pattern, course_referal_url_generator).group(1)

    logger.error(f'не удалось получить ссылку на курс для {course_referal_url}')
    return course_referal_url


@logger.catch
def _render_course_start_date(course_row_data):
    """  функция определения даты начала курса """
    start_date_row_data = course_row_data['data-date']
    if start_date_row_data == "0":
        return None
    else:
        return str(datetime.fromtimestamp(int(start_date_row_data)).date())


@logger.catch
def write_data(data):
    with open('tutortop_course_data.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        for row in data:
            writer.writerow(row)
