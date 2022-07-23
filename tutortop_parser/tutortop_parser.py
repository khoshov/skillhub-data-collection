import csv
import re
from datetime import date, datetime
from time import sleep
from typing import Dict, Optional

from bs4 import BeautifulSoup

from base_func.http_requests import fetch_html, send_parse_data
from settings.logger_settings import logger
from settings.mapping import COURSE_DURATION_TYPE


@logger.catch
def load_main_page_course_links(home_page_url: str) -> Dict:
    """ фунция собирает ссылки на разделы с курсами с главной страницы """
    courses_links = {}
    home_page_soup_data = BeautifulSoup(fetch_html(home_page_url).text, 'lxml')
    courses_catalog = home_page_soup_data.select_one(".submenu__wrap__right__425 .submenu__wrap__mark").select("a")
    for item in courses_catalog[1:]:
        courses_links[item.get_text()] = item['href']
    return courses_links


@logger.catch
def load_courses_data_by_category_url(url: str, course_category: str) -> None:
    """ функция собирает дынные о платных и бесплатных курсах в категории """
    courses_page_soup_data = BeautifulSoup(fetch_html(url).text, 'lxml')
    fetch_all_paid_courses_data_by_category(courses_page_soup_data, course_category)
    # fetch_all_free_courses_data_by_category(courses_page_soup_data, course_category)
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
            "course_duration": float(course_item['data-dlitelnost'].replace(',', '.')),
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
def _find_course_url(course_row_data: str) -> Optional[str]:
    """ Search course link in affilate url """
    course_referal_url = course_row_data.select_one('a.tab-link-course')['href']
    # if url is not affilated
    if 'goto' not in course_referal_url and 'gooto' not in course_referal_url:
        return course_referal_url

    base_url = 'https://tutortop.ru'
    # check if course_referal_url doesn't contain 'https://tutortop.ru'
    course_referal_url = course_referal_url if base_url in course_referal_url else base_url + course_referal_url
    # replace special html entity
    course_referal_url = course_referal_url.replace("&amp;", "&")
    course_referal_data = fetch_html(course_referal_url)
    if course_referal_data:
        course_url = course_referal_data.url
        # if redirection is forbidden
        if base_url in course_url:
            re_patterns = [
                r"\?dl=(.+?)(';|#|\?ref|&subid)",
                r"ulp=(.+)';",
                r"href\s*?=\s*?\\*?'(.+?)(\?unit|'|\?utm|\?ref)"
            ]
            for pattern in re_patterns:
                if re.search(pattern, course_referal_data.text):
                    return re.search(pattern, course_referal_data.text).group(1)
            logger.error(f'Не удалось найти ссылку на курс регулярным выражением по url = {course_referal_url}')

        re_patterns = [r"(https://.+?)\?"]
        for pattern in re_patterns:
            if re.search(pattern, course_url):
                return re.search(pattern, course_url).group(1)
        return course_url

    logger.error(f'не удалось получить ссылку на курс для {course_referal_url}')
    return None


@logger.catch
def _render_course_start_date(course_row_data):
    """  функция определения даты начала курса """
    start_date_row_data = course_row_data['data-date']
    if not start_date_row_data:
        return str(date(1970, 1, 1))
    if start_date_row_data == "0":
        return None
    else:
        return str(datetime.fromtimestamp(int(start_date_row_data)).date())


@logger.catch
def write_data(data):
    with open('tutortop_course_data.csv', 'a', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(data)
